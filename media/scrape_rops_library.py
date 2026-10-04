"""Scrapes the ROPS Kraków social innovation library into media/.

https://rops.krakow.pl/innowacje-spoleczne/biblioteka-innowacji-spolecznych/kategorie

For every innovation in every category it reads the detail page (description sections,
authors, program, licence, film, QR) and the "pobierz materiały" zip. The zips hold the
real documents (final model, test reports, specifications) but weigh ~82 GB in total,
mostly films and app source code, so they are never downloaded whole: the zip directory
and single members are read with HTTP range requests.

Outputs (relative to this file):
  innovations.json              one record per innovation
  pdf/<slug>/<name>.pdf         every PDF: linked from the page or found in the materials zip
  docs/<slug>/<name>.docx       Word/ODT documents that have no PDF twin
  pdf_text/<slug>/<name>.txt    plain text of each document (review, rag)
  photos/<slug>/<slug>-NN.ext   images from the documents and image files in the zip;
                                logos, banner strips, blanks and near-duplicates dropped
  scrape_report.json            totals, broken links, skipped archives, dropped images

deps: beautifulsoup4, pymupdf. run: python media/scrape_rops_library.py
http responses are cached in media/.cache (gitignored), so re-runs are cheap.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import shutil
import struct
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
import zipfile
import zlib
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath

import fitz
from bs4 import BeautifulSoup, NavigableString, Tag

BASE = "https://rops.krakow.pl"
INDEX = f"{BASE}/innowacje-spoleczne/biblioteka-innowacji-spolecznych/kategorie"
LIB_PATH = "/innowacje-spoleczne/biblioteka-innowacji-spolecznych/"
UA = "Mozilla/5.0 (HackYeah2026 ROPS hub; data import for the innovation library)"
DELAY_S = 0.3

ROOT = Path(__file__).resolve().parent
CACHE = ROOT / ".cache"
OUT_DIRS = {name: ROOT / name for name in ("pdf", "docs", "pdf_text", "photos")}

# nested archives up to this size are opened (they hold the model documents);
# bigger ones are films or app source code and are only listed
NESTED_ZIP_MAX = 100 * 1024 * 1024
# documents bigger than this are not downloaded (none of the real ones are)
DOC_MAX = 80 * 1024 * 1024

MIN_IMAGE_SIDE = 150
MIN_ZIP_IMAGE_SIDE = 300
MAX_ASPECT = 4.0  # wider/taller strips are logo bars and decorations
# an image covering this share of its page and mostly white is a page of text or a drawing
# saved as a picture, not a photo
FULL_PAGE = 0.8
WHITE_PAGE = 0.5
# photo vs graphic: graphics are mostly white or made of flat fills (identical neighbouring
# pixels); photos always carry noise. calibrated on product photos vs diagrams/pictograms
PHOTO_MAX_WHITE = 0.35
PHOTO_MAX_FLAT = 0.64
LOGO_MIN_INNOVATIONS = 3
# same picture = close dhash (cheap prefilter) + same shape + almost no strongly differing
# pixels on a 64x64 thumbnail. the 64-bit hash alone merges cards printed on one template;
# calibrated: resampled copies differ in <=0.04% of pixels, distinct cards in >=1.7%
DUP_HASH_BITS = 12
DUP_RATIO = 0.03
DUP_PIXEL_DIFF = 48
DUP_MAX_CHANGED = 0.005

ICON_ROLE = {"lupa": "pdf", "play": "video", "read2": "materials", "cc_by": "license", "symbol-c-w-kolku": "license"}
VIDEO_HOSTS = ("youtube.com", "youtu.be", "vimeo.com", "facebook.com/watch", "fb.watch", "dailymotion.com")
VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".wmv", ".m4v", ".webm", ".mpg", ".mpeg"}
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".ogg", ".flac"}
DOC_EXT = {".docx", ".odt"}
IMAGE_EXT = {".jpg", ".jpeg", ".png"}
# image files under these paths are app assets / source code, not pictures of the innovation
CODE_PATH = re.compile(
    r"(\.xcassets|\.lproj|\.framework|\.bundle|/pods/|/res/|drawable|mipmap|node_modules|/assets/icons?|appicon|"
    r"/src/|/build/|/dist/|kod[ _-]?źródłowy|kody[ _-]?źródłowe|source)",
    re.I,
)

SECTION_KEYS = [
    ("solution", r"na czym polega|rozwiązani"),
    ("problem", r"problem"),
    ("target_group", r"grupa docelowa|adresac|odbiorc"),
    ("who_can_use", r"kto może"),
    ("effectiveness", r"czy to działa|efekt|rezultat|skuteczn"),
    ("authors", r"autor|twórc|innowator"),
    ("contact", r"kontakt"),
]

DOC_KINDS = [
    ("final_model", r"model|finaln|końcow|koncow"),
    ("test_report", r"raport.*test|test.*raport|testowani"),
    ("report", r"raport|sprawozdani"),
    ("specification", r"specyfikacj|dokumentacj|instrukcj|wykr[oó]j|projekt wzornicz"),
    ("recommendations", r"rekomendacj"),
    ("presentation", r"prezentacj"),
    ("scenario", r"scenariusz"),
    ("brochure", r"broszur|folder|ulotk|do druku|plakat"),
]


# ---------- http ----------

def _cache_file(key: str, suffix: str) -> Path:
    return CACHE / (hashlib.sha1(key.encode()).hexdigest() + suffix)


def _request(url: str, headers: dict | None = None, method: str = "GET"):
    req = urllib.request.Request(url, headers={"User-Agent": UA, **(headers or {})}, method=method)
    return urllib.request.urlopen(req, timeout=120)


def fetch(url: str, suffix: str = ".html", byte_range: tuple[int, int] | None = None) -> bytes:
    key = url if byte_range is None else f"{url}#{byte_range[0]}-{byte_range[1]}"
    path = _cache_file(key, suffix)
    if path.exists():
        return path.read_bytes()
    headers = {"Range": f"bytes={byte_range[0]}-{byte_range[1]}"} if byte_range else None
    last: Exception | None = None
    for attempt in range(4):
        try:
            with _request(url, headers) as res:
                if byte_range and res.status != 206:
                    raise RuntimeError(f"{url}: server ignored the range request ({res.status})")
                body = res.read()
            if byte_range and len(body) != byte_range[1] - byte_range[0] + 1:
                raise RuntimeError(f"{url}: short range read")
            CACHE.mkdir(parents=True, exist_ok=True)
            path.write_bytes(body)
            time.sleep(DELAY_S)
            return body
        except urllib.error.HTTPError as e:
            if e.code in (403, 404, 410):
                raise
            last = e
        except (urllib.error.URLError, TimeoutError, ConnectionError, RuntimeError) as e:
            last = e
        time.sleep(2 * (attempt + 1))
    assert last is not None
    raise last


def probe(url: str) -> tuple[int | None, int | None]:
    """status and size without the body"""
    try:
        with _request(url, method="HEAD") as res:
            size = res.headers.get("Content-Length")
            return res.status, int(size) if size and size.isdigit() else None
    except urllib.error.HTTPError as e:
        return e.code, None
    except (urllib.error.URLError, TimeoutError, ConnectionError):
        return None, None


def absolute(href: str) -> str:
    url = urllib.parse.urljoin(BASE + "/", href.strip().replace(" ", "%20"))
    if url.startswith("http://rops.krakow.pl"):
        url = "https://" + url[len("http://"):]
    return url


def soup(url: str) -> BeautifulSoup:
    return BeautifulSoup(fetch(url).decode("utf-8", "replace"), "html.parser")


# ---------- remote zip (range requests) ----------

class RangeReader(io.RawIOBase):
    """seekable view of a remote file; only used to read the zip central directory"""

    BLOCK = 1 << 16

    def __init__(self, url: str, size: int) -> None:
        self.url, self.size, self.pos = url, size, 0

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def tell(self) -> int:
        return self.pos

    def seek(self, offset: int, whence: int = 0) -> int:
        self.pos = offset if whence == 0 else self.pos + offset if whence == 1 else self.size + offset
        return self.pos

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        out = b""
        while len(out) < n:
            block = self.pos // self.BLOCK
            start = block * self.BLOCK
            data = fetch(self.url, ".bin", (start, min(self.size, start + self.BLOCK) - 1))
            take = data[self.pos - start : self.pos - start + n - len(out)]
            out += take
            self.pos += len(take)
        return out


def member_name(info: zipfile.ZipInfo) -> str:
    # windows zip tools store polish names in cp852 without the utf-8 flag
    if info.flag_bits & 0x800:
        return info.filename
    raw = info.filename.encode("cp437")
    for enc in ("utf-8", "cp852", "cp1250"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return info.filename


def read_member(url: str, info: zipfile.ZipInfo) -> bytes:
    """one member of a remote zip: local header + data in two range requests, crc checked"""
    header = fetch(url, ".bin", (info.header_offset, info.header_offset + 29))
    sig, *_, name_len, extra_len = struct.unpack("<IHHHHHIIIHH", header)
    if sig != 0x04034B50:
        raise RuntimeError(f"bad local header for {info.filename}")
    start = info.header_offset + 30 + name_len + extra_len
    raw = fetch(url, ".bin", (start, start + info.compress_size - 1)) if info.compress_size else b""
    return _inflate(info, raw)


def _inflate(info: zipfile.ZipInfo, raw: bytes) -> bytes:
    if info.flag_bits & 0x1:
        raise RuntimeError("encrypted member")
    if info.compress_type == zipfile.ZIP_STORED:
        data = raw
    elif info.compress_type == zipfile.ZIP_DEFLATED:
        data = zlib.decompress(raw, -15)
    else:
        raise RuntimeError(f"unsupported compression {info.compress_type}")
    if zlib.crc32(data) & 0xFFFFFFFF != info.CRC:
        raise RuntimeError(f"crc mismatch for {info.filename}")
    return data


@dataclass
class Member:
    path: str  # display path, nested archives as "outer.zip/inner/file.pdf"
    size: int
    load: object  # () -> bytes


def list_remote_zip(url: str, size: int, report: dict, slug: str) -> list[Member]:
    z = zipfile.ZipFile(RangeReader(url, size))
    members: list[Member] = []
    for info in z.infolist():
        if info.is_dir():
            continue
        name = member_name(info)
        if name.lower().endswith(".zip"):
            if info.file_size <= NESTED_ZIP_MAX:
                try:
                    inner = zipfile.ZipFile(io.BytesIO(read_member(url, info)))
                    for sub in inner.infolist():
                        if not sub.is_dir():
                            members.append(
                                Member(f"{name}/{member_name(sub)}", sub.file_size, lambda z=inner, s=sub: z.read(s))
                            )
                    continue
                except (zipfile.BadZipFile, RuntimeError) as e:
                    report["skipped_archives"].append({"innovation": slug, "path": name, "reason": str(e)})
            else:
                report["skipped_archives"].append(
                    {"innovation": slug, "path": name, "bytes": info.file_size, "reason": "too big to open (films / source code)"}
                )
            members.append(Member(name, info.file_size, None))
            continue
        members.append(Member(name, info.file_size, lambda i=info: read_member(url, i)))
    return members


# ---------- text helpers ----------

def clean(text: str) -> str:
    text = text.replace("\xa0", " ").replace("​", "").replace("­", "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    return re.sub(r"\n{3,}", "\n\n", text).strip()


def block_text(el: Tag) -> str:
    parts: list[str] = []
    for node in el.descendants:
        if isinstance(node, NavigableString):
            parts.append(str(node))
        elif node.name == "br":
            parts.append("\n")
        elif node.name == "li":
            parts.append("\n- ")
    return clean("".join(parts))


def safe_name(name: str) -> str:
    stem, ext = PurePosixPath(name).stem, PurePosixPath(name).suffix.lower()
    ascii_stem = unicodedata.normalize("NFKD", stem.replace("ł", "l").replace("Ł", "L")).encode("ascii", "ignore").decode()
    ascii_stem = re.sub(r"[^A-Za-z0-9]+", "-", ascii_stem).strip("-").lower()[:90] or "plik"
    return ascii_stem + ext


def video_info(url: str) -> dict:
    parsed = urllib.parse.urlparse(url)
    host = parsed.netloc.lower().removeprefix("www.").removeprefix("m.")
    info: dict = {"url": url, "platform": "other"}
    if "youtu" in host:
        info["platform"] = "youtube"
        q = urllib.parse.parse_qs(parsed.query)
        vid = parsed.path.strip("/").split("/")[0] if host == "youtu.be" else q.get("v", [None])[0]
        if not vid:
            m = re.search(r"/(?:embed|shorts|live)/([\w-]{11})", url)
            vid = m.group(1) if m else None
        if vid:
            info.update(
                youtube_id=vid,
                watch_url=f"https://www.youtube.com/watch?v={vid}",
                thumbnail_url=f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
            )
        elif q.get("list"):
            info.update(playlist_id=q["list"][0], watch_url=f"https://www.youtube.com/playlist?list={q['list'][0]}")
    elif "vimeo" in host:
        info["platform"] = "vimeo"
    elif "facebook" in host or host == "fb.watch":
        info["platform"] = "facebook"
    return info


def is_video_url(url: str) -> bool:
    low = url.lower()
    return any(h in low for h in VIDEO_HOSTS) and "/channel/" not in low and "/@" not in low and "/user/" not in low


def doc_kind(path: str) -> str:
    low = path.lower()
    if re.search(r"za[łl][aą]cznik|aneks", low) and not re.search(r"model.*z za[łl][aą]cznikami", low):
        return "attachment"
    name = PurePosixPath(low).name
    for kind, pattern in DOC_KINDS:
        if re.search(pattern, name):
            return kind
    return "other"


# ---------- model ----------

@dataclass
class Innovation:
    slug: str
    url: str
    title: str = ""
    subtitle: str = ""
    categories: list[dict] = field(default_factory=list)
    program: str | None = None
    problem: str = ""
    solution: str = ""
    target_group: str = ""
    who_can_use: str = ""
    effectiveness: str = ""
    authors: list[str] = field(default_factory=list)
    sections: list[dict] = field(default_factory=list)
    description_markdown: str = ""
    primary_pdf: str | None = None
    documents: list[dict] = field(default_factory=list)
    videos: list[dict] = field(default_factory=list)
    video_files: list[dict] = field(default_factory=list)
    audio_files: list[dict] = field(default_factory=list)
    cover_photo: str | None = None
    photos: list[dict] = field(default_factory=list)
    materials: list[dict] = field(default_factory=list)
    license: dict | None = None
    qr_code_url: str | None = None
    category_icon_url: str | None = None
    other_links: list[dict] = field(default_factory=list)
    issues: list[str] = field(default_factory=list)
    # not exported: links found on the page before download
    _page_pdfs: list[str] = field(default_factory=list)


# ---------- listing ----------

def categories() -> list[dict]:
    page = soup(INDEX)
    seen: dict[str, dict] = {}
    for a in page.select(f'a[href*="{LIB_PATH}"]'):
        url = absolute(a["href"]).split("#")[0].rstrip("/")
        slug = url.rsplit("/", 1)[-1]
        if "," in slug or not slug.startswith("dla-"):
            continue
        seen.setdefault(slug, {"slug": slug, "url": url, "name": ""})
    return sorted(seen.values(), key=lambda c: c["slug"])


def listing(cat: dict) -> list[dict]:
    page = soup(cat["url"])
    title = page.select_one("h2.page-title")
    cat["name"] = clean(title.get_text()) if title else cat["slug"]
    if page.select(".pagination a, a[rel=next]"):
        raise RuntimeError(f"{cat['url']} is paginated; the scraper reads one page only")
    items = []
    for item in page.select(".news-list__item"):
        a = item.select_one("a.news-list__title")
        if not a:
            continue
        desc = item.select_one(".news-list__desc")
        first = desc.find("p") if desc else None
        items.append({"url": absolute(a["href"]), "title": clean(a.get_text()), "subtitle": clean(first.get_text(" ")) if first else ""})
    return items


# ---------- detail page ----------

def parse_detail(inv: Innovation) -> None:
    page = soup(inv.url)
    main = page.select_one(".content__main")
    body = main.select_one(".text-content") if main else None
    if body is None:
        inv.issues.append("detail page has no content block")
        return
    title = main.select_one("h2.page-title")
    if title:
        inv.title = clean(title.get_text())

    for strong in body.find_all("strong"):
        t = clean(strong.get_text(" "))
        m = re.search(r"PROJEKTU\s*[\"„”“]?(.+?)[\"”“]?\s*$", t, re.I)
        if m and "INNOWACJA" in t.upper():
            inv.program = m.group(1).strip(" \"„”“")
            strong.find_parent("p").decompose() if strong.find_parent("p") else None
            break

    for table in body.find_all("table"):
        for a in table.find_all("a", href=True):
            img = a.find("img")
            icon = PurePosixPath(urllib.parse.urlparse(img["src"]).path).stem.lower() if img else ""
            role = next((r for k, r in ICON_ROLE.items() if icon.startswith(k)), None)
            add_link(inv, absolute(a["href"]), role, clean(a.get_text(" ")))
        for img in table.find_all("img"):
            src = absolute(img["src"])
            name = PurePosixPath(urllib.parse.urlparse(src).path).name.lower()
            if "/iKONY_na_www/" in src and name.startswith("a_"):
                inv.category_icon_url = src
            elif "/BIBLIOTEKA_INNOWACJI_SPOECZNYCH/" in src and img.find_parent("a") is None:
                inv.qr_code_url = src
        table.decompose()

    for a in body.find_all("a", href=True):
        add_link(inv, absolute(a["href"]), None, clean(a.get_text(" ")))

    parse_sections(inv, body)


def add_link(inv: Innovation, url: str, role: str | None, text: str) -> None:
    low = url.lower().split("?")[0]
    if url.startswith(("mailto:", "tel:", "#")):
        return
    if LIB_PATH in url and "," not in url:
        return  # back link to the category page (the category icon)
    if role is None:
        if is_video_url(url):
            role = "video"
        elif low.endswith(".pdf"):
            role = "pdf"
        elif low.endswith((".zip", ".rar", ".7z")):
            role = "materials"
        elif "creativecommons.org" in low:
            role = "license"
        else:
            role = "other"
    if role == "pdf" and "zasady_wykorzystania" in low:
        role = "license"
    if role == "license":
        inv.license = inv.license or license_info(url)
    elif role == "pdf":
        if url not in inv._page_pdfs:
            inv._page_pdfs.append(url)
    elif role == "video":
        if not is_video_url(url):
            inv.issues.append(f"film icon points to a non-video page: {url}")
            inv.other_links.append({"url": url, "text": text or "zobacz film"})
        elif not any(v["url"] == url for v in inv.videos):
            inv.videos.append({**video_info(url), "found_in": "page"})
    elif role == "materials":
        if not any(m["url"] == url for m in inv.materials):
            inv.materials.append({"url": url})
    elif not any(o["url"] == url for o in inv.other_links):
        inv.other_links.append({"url": url, "text": text})


def license_info(url: str) -> dict:
    m = re.search(r"creativecommons\.org/licenses/([\w-]+)/([\d.]+)", url)
    if m:
        return {"name": f"CC {m.group(1).upper()} {m.group(2)}", "url": url}
    if "zasady_wykorzystania" in url.lower():
        return {"name": "Zasady wykorzystania innowacji (ROPS, MIIS)", "url": url}
    return {"name": "inna", "url": url}


def parse_sections(inv: Innovation, body: Tag) -> None:
    current: dict | None = None
    intro: list[str] = []

    def heading_of(el: Tag) -> str | None:
        if el.name in ("h2", "h3", "h4", "h5"):
            return clean(el.get_text(" "))
        if el.name == "p":
            strong = el.find(["strong", "b"])
            t = clean(el.get_text(" "))
            if strong and clean(strong.get_text(" ")) == t and re.match(r"^\d+\s*[.)]\s*\S", t):
                return t
        return None

    for el in body.children:
        if not isinstance(el, Tag):
            continue
        h = heading_of(el)
        if h:
            current = {"heading": re.sub(r"^\d+\s*[.)]\s*", "", h).strip(), "text": ""}
            inv.sections.append(current)
            continue
        text = block_text(el)
        if not text:
            continue
        if current is None:
            intro.append(text)
        else:
            current["text"] = (current["text"] + "\n" + text).strip()

    if intro:
        inv.sections.insert(0, {"heading": "Wprowadzenie", "text": "\n".join(intro)})
    for s in inv.sections:
        s["key"] = next((k for k, p in SECTION_KEYS if re.search(p, s["heading"].lower())), "other")
        if s["key"] in ("problem", "solution", "target_group", "who_can_use", "effectiveness") and s["text"]:
            setattr(inv, s["key"], (getattr(inv, s["key"]) + "\n" + s["text"]).strip())
        elif s["key"] == "authors":
            inv.authors += [a.strip(" -–•\t") for a in re.split(r"\n|;", s["text"]) if a.strip(" -–•\t")]

    md = [f"# {inv.title}"]
    if inv.subtitle:
        md.append(f"_{inv.subtitle}_")
    md += [f"## {s['heading']}\n\n{s['text']}" for s in inv.sections if s["text"]]
    inv.description_markdown = "\n\n".join(md)
    for key in ("problem", "solution", "target_group"):
        if not getattr(inv, key):
            inv.issues.append(f"page has no '{key}' section")


# ---------- documents ----------

def unique_path(folder: Path, name: str) -> Path:
    path, n = folder / name, 2
    while path.exists():
        path = folder / f"{PurePosixPath(name).stem}-{n}{PurePosixPath(name).suffix}"
        n += 1
    return path


def save_document(inv: Innovation, data: bytes, original: str, source: dict, seen: dict[str, dict]) -> dict | None:
    digest = hashlib.sha256(data).hexdigest()
    if digest in seen:
        # same file on the page and in the zip: one copy, both sources noted
        seen[digest].setdefault("also_at", []).append(source)
        return None
    ext = PurePosixPath(original).suffix.lower()
    is_pdf = data.startswith(b"%PDF-")
    folder = OUT_DIRS["pdf" if is_pdf else "docs"] / inv.slug
    folder.mkdir(parents=True, exist_ok=True)
    path = unique_path(folder, safe_name(original if is_pdf or ext else original + ".bin"))
    path.write_bytes(data)
    doc = {
        "file": str(path.relative_to(ROOT)),
        "format": "pdf" if is_pdf else ext.lstrip("."),
        "kind": "brochure" if source["from"] == "page" else doc_kind(original),
        "original_name": PurePosixPath(original).name,
        **source,
        "bytes": len(data),
        "sha256": digest,
    }
    text = ""
    if is_pdf:
        try:
            pdf = fitz.open(stream=data, filetype="pdf")
            doc["pages"] = pdf.page_count
            doc["title"] = clean((pdf.metadata or {}).get("title") or "") or None
            text = "\n\n".join(f"--- strona {n + 1} ---\n{p.get_text()}" for n, p in enumerate(pdf))
            for page in pdf:
                for link in page.get_links():
                    uri = link.get("uri")
                    if uri and is_video_url(uri):
                        add_video(inv, uri, f"{doc['file']} s.{page.number + 1}")
            pdf.close()
        except Exception as e:
            inv.issues.append(f"cannot open {doc['file']}: {e}")
    elif ext in DOC_EXT:
        text = office_text(data, ext)
    for uri in re.findall(r"https?://(?:www\.)?(?:youtube\.com/watch\?v=|youtu\.be/)[\w-]{11}", text):
        add_video(inv, uri, f"{doc['file']} (tekst)")
    text = clean(re.sub(r"--- strona \d+ ---\s*(?=--- strona|\Z)", "", text))
    if text.strip():
        tfolder = OUT_DIRS["pdf_text"] / inv.slug
        tfolder.mkdir(parents=True, exist_ok=True)
        tpath = unique_path(tfolder, PurePosixPath(path.name).stem + ".txt")
        tpath.write_text(text, encoding="utf-8")
        doc["text_file"] = str(tpath.relative_to(ROOT))
        doc["text_chars"] = len(text)
    else:
        doc["text_file"] = None
        if is_pdf:
            inv.issues.append(f"{doc['file']} has no text layer (graphics or scan)")
    seen[digest] = doc
    inv.documents.append(doc)
    return doc


def office_text(data: bytes, ext: str) -> str:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
        xml = z.read("word/document.xml" if ext == ".docx" else "content.xml").decode("utf-8", "replace")
    except (zipfile.BadZipFile, KeyError):
        return ""
    xml = re.sub(r"</w:p>|<text:p[^>]*/>|</text:p>|</text:h>", "\n", xml)
    xml = re.sub(r"<w:tab/>|<text:tab/>", "\t", xml)
    return clean(re.sub(r"<[^>]+>", "", xml).replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", '"'))


def add_video(inv: Innovation, url: str, found_in: str) -> None:
    info = video_info(url)
    key = info.get("youtube_id") or url
    if any((v.get("youtube_id") or v["url"]) == key for v in inv.videos):
        return
    inv.videos.append({**info, "found_in": found_in})


def collect_documents(inv: Innovation, report: dict, images: list) -> None:
    seen: dict[str, dict] = {}
    for url in inv._page_pdfs:
        try:
            data = fetch(url, ".pdf")
        except urllib.error.HTTPError as e:
            report["broken_links"].append({"innovation": inv.slug, "kind": "pdf", "url": url, "status": e.code})
            inv.issues.append(f"page pdf returns HTTP {e.code}: {url}")
            continue
        if not data.startswith(b"%PDF-"):
            report["broken_links"].append({"innovation": inv.slug, "kind": "pdf", "url": url, "status": "not a pdf"})
            inv.issues.append(f"page pdf link serves something else: {url}")
            continue
        name = urllib.parse.unquote(PurePosixPath(urllib.parse.urlparse(url).path).name)
        save_document(inv, data, name, {"from": "page", "source_url": url}, seen)

    for m in inv.materials:
        status, size = probe(m["url"])
        m.update(http_status=status, bytes=size)
        if status != 200 or not size:
            report["broken_links"].append({"innovation": inv.slug, "kind": "materials", "url": m["url"], "status": status})
            inv.issues.append(f"materials zip returns HTTP {status}")
            continue
        try:
            members = list_remote_zip(m["url"], size, report, inv.slug)
        except (zipfile.BadZipFile, RuntimeError, urllib.error.URLError) as e:
            inv.issues.append(f"materials zip unreadable: {e}")
            continue
        m["files"] = len(members)
        m["contents"] = [{"path": x.path, "bytes": x.size} for x in members if not _is_code(x.path)]
        m["code_files_omitted"] = sum(_is_code(x.path) for x in members)
        if not members:
            inv.issues.append("materials zip is empty")

        stems_with_pdf = {str(PurePosixPath(x.path).with_suffix("")).lower() for x in members if x.path.lower().endswith(".pdf")}
        for x in members:
            ext = PurePosixPath(x.path).suffix.lower()
            source = {"from": "materials", "source_url": m["url"], "zip_path": x.path}
            if ext in VIDEO_EXT and not _is_code(x.path):
                # a film inside a nested zip needs that whole inner archive to be downloaded
                inv.video_files.append({"zip_url": m["url"], "zip_path": x.path, "bytes": x.size, "nested_in_archive": ".zip/" in x.path.lower()})
            elif ext in VIDEO_EXT:
                continue  # demo clip bundled with app source code
            elif ext in AUDIO_EXT and not _is_code(x.path):
                inv.audio_files.append({"zip_url": m["url"], "zip_path": x.path, "bytes": x.size})
            elif x.load is None:
                continue  # big nested archive, listed in the report
            elif ext == ".pdf" or (ext in DOC_EXT and str(PurePosixPath(x.path).with_suffix("")).lower() not in stems_with_pdf):
                if x.size > DOC_MAX:
                    inv.issues.append(f"skipped {x.path}: {x.size // 2**20} MB")
                    continue
                try:
                    data = x.load()
                except Exception as e:
                    inv.issues.append(f"cannot read {x.path} from the zip: {e}")
                    continue
                doc = save_document(inv, data, x.path, source, seen)
                if doc and doc["format"] in ("docx", "odt"):
                    images += [(inv, f"{doc['file']}", None, b) for b in office_images(data)]
            elif ext in IMAGE_EXT and not _is_code(x.path) and x.size >= 30_000:
                try:
                    images.append((inv, f"{m['url']}::{x.path}", None, x.load()))
                except Exception as e:
                    inv.issues.append(f"cannot read {x.path} from the zip: {e}")

    for v in inv.videos:
        if v.get("watch_url"):
            status, _ = probe(f"https://www.youtube.com/oembed?url={urllib.parse.quote(v['watch_url'])}&format=json")
            v["available"] = status == 200
            if status != 200:
                report["broken_links"].append({"innovation": inv.slug, "kind": "video", "url": v["url"], "status": status})

    pdfs = [d for d in inv.documents if d["format"] == "pdf"]
    rank = {"brochure": 0, "final_model": 1}
    pdfs.sort(key=lambda d: (rank.get(d["kind"], 5), d.get("zip_path", "").count("/"), -d.get("text_chars", 0)))
    inv.primary_pdf = pdfs[0]["file"] if pdfs else None
    for d in inv.documents:
        d["is_primary"] = d["file"] == inv.primary_pdf
    if not pdfs:
        inv.issues.append("no pdf at all (page or materials)")
    for d in pdfs:
        images.append((inv, d["file"], ROOT / d["file"], None))


def _is_code(path: str) -> bool:
    return bool(CODE_PATH.search("/" + path.lower()))


def office_images(data: bytes) -> list[bytes]:
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile:
        return []
    return [z.read(n) for n in z.namelist() if n.lower().startswith(("word/media/", "pictures/")) and n.lower().endswith((".jpg", ".jpeg", ".png"))]


# ---------- images ----------

def _gray(pix: fitz.Pixmap) -> fitz.Pixmap:
    gray = fitz.Pixmap(fitz.csGRAY, pix) if pix.n - pix.alpha != 1 else pix
    return fitz.Pixmap(gray, 0) if gray.alpha else gray


def dhash(pix: fitz.Pixmap) -> int:
    """difference hash on an area-averaged 9x8 thumbnail, stable across resolutions"""
    s = fitz.Pixmap(_gray(pix), 9, 8, None).samples
    bits = 0
    for y in range(8):
        for x in range(8):
            bits = (bits << 1) | (s[y * 9 + x] > s[y * 9 + x + 1])
    return bits


def measure(pix: fitz.Pixmap) -> dict:
    """whiteness on the full image (thumbnails blur text into grey), the rest on thumbnails"""
    full = _gray(pix).samples
    sample = full[:: max(1, len(full) // 20000)]
    white = sum(v >= 235 for v in sample) / max(1, len(sample))

    rgb = pix if pix.n - pix.alpha == 3 else fitz.Pixmap(fitz.csRGB, pix)
    if rgb.alpha:
        rgb = fitz.Pixmap(rgb, 0)
    t = fitz.Pixmap(rgb, 128, 128, None).samples
    flat = sum(
        abs(t[i] - t[i + 3]) <= 2 and abs(t[i + 1] - t[i + 4]) <= 2 and abs(t[i + 2] - t[i + 5]) <= 2
        for row in range(128)
        for i in range(row * 384, row * 384 + 381, 3)
    ) / (128 * 127)

    small = fitz.Pixmap(rgb, 64, 64, None)
    if small.alpha:
        small = fitz.Pixmap(small, 0)
    if small.n == 1:
        small = fitz.Pixmap(fitz.csRGB, small)
    px = small.samples
    rg, yb, gray = [], [], []
    for i in range(0, len(px), 3):
        r, g, b = px[i], px[i + 1], px[i + 2]
        rg.append(r - g)
        yb.append((r + g) / 2 - b)
        gray.append((r * 299 + g * 587 + b * 114) // 1000)

    def mean_std(v: list) -> tuple[float, float]:
        m = sum(v) / len(v)
        return m, (sum((x - m) ** 2 for x in v) / len(v)) ** 0.5

    (mrg, srg), (myb, syb) = mean_std(rg), mean_std(yb)
    return {
        "white": white,
        "flat": flat,
        # hasler & suesstrunk colourfulness
        "colour": (srg**2 + syb**2) ** 0.5 + 0.3 * (mrg**2 + myb**2) ** 0.5,
        "detail": sum(abs(gray[i] - gray[i + 1]) for i in range(len(gray) - 1) if (i + 1) % 64) / (63 * 64),
        # almost no mid tones: qr codes, line drawings, scanned text
        "bilevel": sum(40 < v < 215 for v in gray) / len(gray) < 0.12,
        "spread": max(gray) - min(gray),
    }


def is_paper_shape(pix: fitz.Pixmap) -> bool:
    """a-series sheet (1:sqrt 2): mostly-white images of this shape are page previews"""
    r = pix.width / pix.height
    return abs(r - 0.7071) < 0.025 or abs(r - 1.4142) < 0.05


def to_rgb(pix: fitz.Pixmap) -> fitz.Pixmap:
    if pix.colorspace and pix.colorspace.n > 3:
        pix = fitz.Pixmap(fitz.csRGB, pix)
    return pix


def pdf_images(path: Path) -> list[tuple[int, fitz.Pixmap, bytes, str, float]]:
    out = []
    doc = fitz.open(path)
    seen_xref: set[int] = set()
    for page in doc:
        for img in page.get_images(full=True):
            xref, smask = img[0], img[1]
            if xref in seen_xref:
                continue
            seen_xref.add(xref)
            try:
                info = doc.extract_image(xref)
                if not info or min(info["width"], info["height"]) < MIN_IMAGE_SIDE:
                    continue
                pix = to_rgb(fitz.Pixmap(doc, xref))
                masked = False
                if smask:
                    try:
                        base = fitz.Pixmap(pix, 0) if pix.alpha else pix
                        pix = fitz.Pixmap(base, fitz.Pixmap(doc, smask))
                        masked = True
                    except Exception:
                        pass  # keep the image without its transparency
                cmyk = info.get("colorspace") == 4
                if info["ext"] in ("jpeg", "jpg") and not masked and not cmyk:
                    data, ext = info["image"], "jpg"
                elif info["ext"] == "png" and not masked:
                    data, ext = info["image"], "png"
                else:
                    data, ext = pix.tobytes("png"), "png"
                page_area = abs(page.rect) or 1
                coverage = max((abs(r & page.rect) for r in page.get_image_rects(xref)), default=0) / page_area
                out.append((page.number + 1, pix, data, ext, coverage))
            except Exception:
                continue
    doc.close()
    return out


def same_picture(a: dict, b: dict) -> bool:
    if bin(a["dhash"] ^ b["dhash"]).count("1") > DUP_HASH_BITS:
        return False
    ra, rb = a["w"] / a["h"], b["w"] / b["h"]
    if abs(ra - rb) / max(ra, rb) > DUP_RATIO:
        return False
    changed = sum(abs(x - y) > DUP_PIXEL_DIFF for x, y in zip(a["thumb"], b["thumb"]))
    return changed / len(a["thumb"]) < DUP_MAX_CHANGED


def process_images(images: list, report: dict) -> None:
    candidates: list[dict] = []
    for inv, source, pdf_path, raw in images:
        if pdf_path is not None:
            items = pdf_images(pdf_path)
        else:
            try:
                pix = to_rgb(fitz.Pixmap(raw))
            except Exception:
                report["dropped_images"]["unreadable"] += 1
                continue
            ext = "png" if raw[:4] == b"\x89PNG" else "jpg"
            min_side = MIN_ZIP_IMAGE_SIDE if "::" in source else MIN_IMAGE_SIDE
            if min(pix.width, pix.height) < min_side:
                report["dropped_images"]["too_small"] += 1
                continue
            items = [(None, pix, raw, ext, 0.0)]
        for page, pix, data, ext, coverage in items:
            if max(pix.width, pix.height) / max(1, min(pix.width, pix.height)) > MAX_ASPECT:
                report["dropped_images"]["strip_or_banner"] += 1
                continue
            m = measure(pix)
            if m["spread"] < 12:
                report["dropped_images"]["blank"] += 1
                continue
            if m["white"] >= WHITE_PAGE and (coverage >= FULL_PAGE or is_paper_shape(pix)):
                report["dropped_images"]["page_of_text_or_drawing"] += 1
                continue
            # sizes and metrics only: holding every pixmap would need gigabytes
            candidates.append(
                {
                    "inv": inv, "source": source, "page": page, "w": pix.width, "h": pix.height,
                    "data": data, "ext": ext, "sha": hashlib.sha256(data).hexdigest(), "dhash": dhash(pix),
                    "thumb": fitz.Pixmap(_gray(pix), 64, 64, None).samples,
                    "kind": "photo" if m["white"] < PHOTO_MAX_WHITE and m["flat"] < PHOTO_MAX_FLAT and not m["bilevel"] else "graphic",
                    **m,
                }
            )

    # logos: the same picture in the documents of several innovations
    for c in candidates:
        owners = {c["inv"].slug}
        for o in candidates:
            if o["inv"].slug not in owners and same_picture(c, o):
                owners.add(o["inv"].slug)
        c["logo"] = len(owners) >= LOGO_MIN_INNOVATIONS

    kept: dict[str, list] = {}
    # biggest first, so of near-duplicates the best resolution stays
    for c in sorted(candidates, key=lambda c: -(c["w"] * c["h"])):
        if c["logo"]:
            report["dropped_images"]["logo_shared_by_innovations"] += 1
            continue
        mine = kept.setdefault(c["inv"].slug, [])
        if any(same_picture(c, k) for k in mine):
            report["dropped_images"]["duplicate"] += 1
            continue
        mine.append(c)

    for slug_items in kept.values():
        # document order, so photos follow the pdf
        slug_items.sort(key=lambda c: (c["source"], c["page"] or 0))
        inv = slug_items[0]["inv"]
        for n, c in enumerate(slug_items, 1):
            folder = OUT_DIRS["photos"] / inv.slug
            folder.mkdir(parents=True, exist_ok=True)
            name = f"{inv.slug}-{n:02d}.{c['ext']}"
            (folder / name).write_bytes(c["data"])
            entry = {
                "file": f"photos/{inv.slug}/{name}", "kind": c["kind"], "width": c["w"], "height": c["h"],
                "bytes": len(c["data"]), "sha256": c["sha"],
            }
            if "::" in c["source"]:
                url, path = c["source"].split("::", 1)
                entry.update(source="materials", zip_url=url, zip_path=path)
            else:
                entry.update(source="document", document=c["source"], page=c["page"])
            inv.photos.append(entry)
        inv.cover_photo = pick_cover(slug_items, inv.photos)


def pick_cover(items: list[dict], photos: list[dict]) -> str | None:
    """a real, colourful, detailed photo of card-like shape; graphics only when there is no photo.
    items and photos are parallel lists (metrics / exported entries)"""
    def score(c: dict) -> tuple:
        ratio = c["w"] / c["h"]
        return (
            c["kind"] == "photo",
            0.6 <= ratio <= 1.9,
            min(c["w"], c["h"]) >= 300,
            min(c["colour"], 80) / 80 + min(c["detail"], 25) / 25,
        )
    # only real photos: a logo, coat of arms or qr code is a worse cover than none
    # (the frontend falls back to the category icon)
    usable = [i for i in range(len(items)) if items[i]["kind"] == "photo"]
    if not usable:
        return None
    return photos[max(usable, key=lambda i: score(items[i]))]["file"]


# ---------- main ----------

def export(inv: Innovation) -> dict:
    data = {k: v for k, v in vars(inv).items() if not k.startswith("_")}
    data["category_slugs"] = [c["slug"] for c in inv.categories]
    return data


def main() -> int:
    return run()


def run(only_slugs: set[str] | None = None) -> int:
    """only_slugs: process just these innovations (output is rewritten for them only)"""
    for d in OUT_DIRS.values():
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True)
    report: dict = {
        "summary": {},
        "broken_links": [],
        "skipped_archives": [],
        "dropped_images": Counter(),
        "title_differs_from_listing": [],
    }

    cats = categories()
    by_slug: dict[str, Innovation] = {}
    listed = 0
    for cat in cats:
        items = listing(cat)
        print(f"{cat['slug']}: {len(items)}", file=sys.stderr)
        for it in items:
            listed += 1
            slug = urllib.parse.urlparse(it["url"]).path.rsplit(",", 1)[-1].strip("/")
            inv = by_slug.setdefault(slug, Innovation(slug=slug, url=it["url"], title=it["title"], subtitle=it["subtitle"]))
            if not any(c["slug"] == cat["slug"] for c in inv.categories):
                inv.categories.append({"slug": cat["slug"], "name": cat["name"]})

    innovations = sorted((i for i in by_slug.values() if only_slugs is None or i.slug in only_slugs), key=lambda i: i.slug)
    images: list = []
    for n, inv in enumerate(innovations, 1):
        print(f"[{n}/{len(innovations)}] {inv.slug}", file=sys.stderr)
        listing_title = inv.title
        try:
            parse_detail(inv)
        except urllib.error.HTTPError as e:
            inv.issues.append(f"detail page HTTP {e.code}")
            report["broken_links"].append({"innovation": inv.slug, "kind": "page", "url": inv.url, "status": e.code})
            continue
        if listing_title.lower() != inv.title.lower():
            report["title_differs_from_listing"].append({"slug": inv.slug, "listing": listing_title, "page": inv.title})
        collect_documents(inv, report, images)

    print("images...", file=sys.stderr)
    process_images(images, report)

    docs = [d for i in innovations for d in i.documents]
    report["summary"] = {
        "categories": len(cats),
        "listing_entries": listed,
        "innovations": len(innovations),
        "in_several_categories": sum(len(i.categories) > 1 for i in innovations),
        "with_primary_pdf": sum(bool(i.primary_pdf) for i in innovations),
        "pdf_files": sum(d["format"] == "pdf" for d in docs),
        "docx_odt_files": sum(d["format"] != "pdf" for d in docs),
        "documents_bytes": sum(d["bytes"] for d in docs),
        "with_online_video": sum(bool(i.videos) for i in innovations),
        "online_videos": sum(len(i.videos) for i in innovations),
        "online_videos_unavailable": sum(v.get("available") is False for i in innovations for v in i.videos),
        "with_video_files_in_materials": sum(bool(i.video_files) for i in innovations),
        "video_files_in_materials": sum(len(i.video_files) for i in innovations),
        "video_files_bytes": sum(v["bytes"] for i in innovations for v in i.video_files),
        "photos": sum(len(i.photos) for i in innovations),
        "innovations_with_photos": sum(bool(i.photos) for i in innovations),
        "with_issues": sum(bool(i.issues) for i in innovations),
    }
    report["dropped_images"] = dict(report["dropped_images"])
    out = {
        "source": INDEX,
        "scraped_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "paths_relative_to": "media/",
        "categories": cats,
        "innovations": [export(i) for i in innovations],
    }
    (ROOT / "innovations.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    (ROOT / "scrape_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())

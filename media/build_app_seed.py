"""Turns the scraped library (media/innovations.json) into app seed data.

Writes:
  rag/sql/008_seed_rops_library.sql      innovations rows (rag's table), embedded by `seed-embed`
  backend/sql/012_innovation_profiles.sql match-api's innovation_profiles table + its rows
  backend/seed_media/<id>/photo-N.jpg    two photos per innovation, resized
  backend/seed_media/<id>/document.pdf   the main pdf, unchanged (downloaded whole)

ON CONFLICT DO NOTHING everywhere: re-running the migration keeps admin edits.
deps: pymupdf (same venv as scrape_rops_library.py). run: python media/build_app_seed.py
"""

from __future__ import annotations

import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

import fitz

sys.path.insert(0, str(Path(__file__).resolve().parent))
import scrape_rops_library as scraper  # noqa: E402

MEDIA = Path(__file__).resolve().parent
REPO = MEDIA.parent
SEED_MEDIA = REPO / "backend" / "seed_media"
RAG_SQL = REPO / "rag" / "sql" / "008_seed_rops_library.sql"
PROFILE_SQL = REPO / "backend" / "sql" / "012_innovation_profiles.sql"

PHOTOS_PER_INNOVATION = 2
PHOTO_MAX_SIDE = 1280
PHOTO_QUALITY = 80
# the pdf is downloaded whole, as published; only a print-ready duplicate is swapped for
# the smaller version of the same document
PDF_PREFER_SMALLER_ABOVE = 4 * 1024 * 1024

# ROPS library category -> the 8 Mapa Wyzwań challenge areas used by the app
CATEGORY_AREA = {
    "dla-cudzoziemcow": "Integracja cudzoziemcow",
    "dla-dzieci-mlodziezy-i-rodziny": "Rodzina i piecza zastepcza",
    "dla-osob-o-ograniczonej-mobilnosci": "Niepelnosprawnosc",
    "dla-osob-w-kryzysie-bezdomnosci": "Bezdomnosc",
    "dla-osob-z-niepelnosprawnoscia-intelektualna": "Niepelnosprawnosc",
    "dla-osob-z-niepelnosprawnoscia-sensoryczna": "Niepelnosprawnosc",
    # labour market activation is the app's poverty / exclusion area
    "dla-rynku-pracy": "Ubostwo",
    "dla-seniorow": "Seniorzy",
    "dla-zdrowia-i-medycyny": "Zdrowie",
}

# the scraped slug of an innovation already seeded under another id (rag/sql/007)
ALIASES = {"hop-hop-mobilny-plac-zabaw": "hop-hop"}


def q(text: str | None) -> str:
    return "NULL" if text is None else "'" + text.replace("'", "''") + "'"


def arr(items: list[str]) -> str:
    return "ARRAY[" + ", ".join(q(i) for i in items) + "]::text[]" if items else "'{}'::text[]"


def area_tag(area: str) -> str:
    # same slug as backend/app/services/admin/innovation_upload.py, which reads these tags back
    ascii_text = unicodedata.normalize("NFKD", area).encode("ascii", "ignore").decode()
    return "area:" + re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")


def content(inv: dict) -> str:
    """the text rag embeds: the same labelled layout as the 007 seed"""
    parts = [
        ("Problem", inv["problem"]),
        ("Rozwiązanie", inv["solution"]),
        ("Dla kogo", inv["target_group"]),
        ("Kto może skorzystać", inv["who_can_use"]),
        ("Czy to działa", inv["effectiveness"]),
        ("Autorzy", ", ".join(inv["authors"])),
        ("Program", inv["program"] or ""),
    ]
    body = "\n\n".join(f"{k}: {v}" for k, v in parts if v)
    return body + "\n\nŹródło: Biblioteka innowacji społecznych ROPS w Krakowie."


def tagline(inv: dict) -> str | None:
    sub = (inv["subtitle"] or "").strip()
    # "BaWita - tablica ..." -> "tablica ..."
    sub = re.sub(rf"^{re.escape(inv['title'])}\s*[-–—:]\s*", "", sub, flags=re.I).strip()
    if not sub or sub.upper().startswith("INNOWACJA WYBRANA"):
        return None
    return sub[0].upper() + sub[1:]


def video_url(inv: dict) -> str | None:
    videos = [v for v in inv["videos"] if v.get("available") and v.get("watch_url")]
    # the page's own film first, then films linked from the documents; single films before playlists
    videos.sort(key=lambda v: (v["found_in"] != "page", "playlist_id" in v))
    return videos[0]["watch_url"] if videos else None


def pick_photos(inv: dict) -> list[dict]:
    photos = inv["photos"]
    if not photos:
        return []
    metrics = {}
    for p in photos:
        pix = scraper.to_rgb(fitz.Pixmap(str(MEDIA / p["file"])))
        metrics[p["file"]] = scraper.measure(pix)
    real = [p for p in photos if p["kind"] == "photo"]
    # without photos fall back to graphics with real content (no qr codes / line drawings)
    pool = real or [p for p in photos if not metrics[p["file"]]["bilevel"] and min(p["width"], p["height"]) >= 300]

    def score(p: dict) -> tuple:
        m, ratio = metrics[p["file"]], p["width"] / p["height"]
        return (0.6 <= ratio <= 1.9, min(p["width"], p["height"]) >= 400, min(m["colour"], 80) / 80 + min(m["detail"], 25) / 25)

    chosen: list[dict] = []
    if inv["cover_photo"] and any(p["file"] == inv["cover_photo"] for p in pool):
        chosen.append(next(p for p in pool if p["file"] == inv["cover_photo"]))
    for p in sorted(pool, key=score, reverse=True):
        if len(chosen) >= PHOTOS_PER_INNOVATION:
            break
        # a second picture from another page, so the two do not show the same thing
        if p in chosen or any(p.get("document") == c.get("document") and p.get("page") == c.get("page") for c in chosen):
            continue
        chosen.append(p)
    return chosen


def save_photo(src: Path, dest: Path) -> None:
    pix = scraper.to_rgb(fitz.Pixmap(str(src)))
    if pix.alpha:
        # jpeg has no alpha: blend onto white
        alpha = pix.samples[pix.n - 1 :: pix.n]
        base = fitz.Pixmap(pix, 0).samples
        out = bytearray(len(base))
        for i, a in enumerate(alpha):
            for c in range(3):
                out[i * 3 + c] = (base[i * 3 + c] * a + 255 * (255 - a)) // 255
        pix = fitz.Pixmap(fitz.csRGB, pix.width, pix.height, bytes(out), False)
    scale = min(1.0, PHOTO_MAX_SIDE / max(pix.width, pix.height))
    if scale < 1:
        pix = fitz.Pixmap(pix, int(pix.width * scale), int(pix.height * scale), None)
    dest.write_bytes(pix.tobytes("jpeg", jpg_quality=PHOTO_QUALITY))


def pick_pdf(inv: dict) -> dict | None:
    pdfs = [d for d in inv["documents"] if d["format"] == "pdf"]
    primary = next((d for d in pdfs if d["file"] == inv["primary_pdf"]), None)
    if primary and primary["bytes"] > PDF_PREFER_SMALLER_ABOVE:
        # e.g. "A4 do druku" next to a text version of the same brochure: the smallest pdf
        # that carries at least half of the main document's text
        enough = primary.get("text_chars", 0) / 2
        smaller = [d for d in pdfs if d["bytes"] < primary["bytes"] and d.get("text_chars", 0) >= max(enough, 1000)]
        if smaller:
            return min(smaller, key=lambda d: d["bytes"])
    return primary


def save_pdf(src: Path, dest: Path) -> int:
    shutil.copyfile(src, dest)
    return dest.stat().st_size


def main() -> int:
    data = json.loads((MEDIA / "innovations.json").read_text(encoding="utf-8"))
    if SEED_MEDIA.exists():
        shutil.rmtree(SEED_MEDIA)
    SEED_MEDIA.mkdir(parents=True)

    rows, profiles, films, total = [], [], [], 0
    for inv in data["innovations"]:
        iid = ALIASES.get(inv["slug"], inv["slug"])
        folder = SEED_MEDIA / iid
        folder.mkdir()

        photo_names = []
        for n, p in enumerate(pick_photos(inv), 1):
            name = f"photo-{n}.jpg"
            save_photo(MEDIA / p["file"], folder / name)
            photo_names.append(name)
            total += (folder / name).stat().st_size

        pdf = pick_pdf(inv)
        if pdf:
            total += save_pdf(MEDIA / pdf["file"], folder / "document.pdf")
        if not any(folder.iterdir()):
            folder.rmdir()

        if video_url(inv):
            films.append(f"UPDATE innovations SET page_url = {q(video_url(inv))} WHERE id = {q(iid)} AND page_url IS NULL;")
        areas = sorted({CATEGORY_AREA[c] for c in inv["category_slugs"]})
        tags = ["type:innovation", *(area_tag(a) for a in areas), "source:rops-biblioteka"]
        rows.append(
            f"    (\n        {q(iid)},\n        {q(inv['title'])},\n        {q(content(inv))},\n"
            f"        {q(inv['solution'])},\n        {arr(tags)},\n        '',\n        {q(video_url(inv))},\n"
            "        'published'\n    )"
        )
        # the page shouts the project name in capitals
        program = inv["program"].title() if inv["program"] else None
        profiles.append(
            f"    (\n        {q(iid)},\n        {q(tagline(inv))},\n        {q(program)},\n"
            f"        {q(inv['problem'] or None)},\n        {q(inv['target_group'] or None)},\n"
            f"        {q(inv['who_can_use'] or None)},\n        {q(inv['effectiveness'] or None)},\n"
            f"        {arr(inv['authors'])},\n        {arr(photo_names)},\n"
            f"        {q((inv['license'] or {}).get('name'))},\n        {q((inv['license'] or {}).get('url'))},\n"
            f"        {q(inv['url'])}\n    )"
        )
        print(f"{iid}: {len(photo_names)} photos, pdf={'yes' if pdf else 'no'}", file=sys.stderr)

    RAG_SQL.write_text(
        "-- innovations from the ROPS social innovation library (rops.krakow.pl), generated by\n"
        "-- media/build_app_seed.py from media/innovations.json; do not edit by hand.\n"
        "-- compose `seed-embed` embeds them; page_url holds the film. ON CONFLICT keeps admin edits\n"
        "-- and the rows 007 already seeds (hop-hop, himalaje-autyzmu, gra-o-zdrowie).\n"
        "INSERT INTO innovations (id, title, content, summary, tags, city, page_url, status)\nVALUES\n"
        + ",\n".join(rows)
        + "\nON CONFLICT (id) DO NOTHING;\n\n"
        "-- rows seeded earlier without a film get it; a film an admin set stays\n"
        + "\n".join(films)
        + "\n",
        encoding="utf-8",
    )
    PROFILE_SQL.write_text(
        "-- per-innovation description that rag's innovations table has no columns for:\n"
        "-- the library page sections, authors, licence and the photos in backend/seed_media/<id>/.\n"
        "CREATE TABLE IF NOT EXISTS innovation_profiles (\n"
        "    innovation_id text PRIMARY KEY REFERENCES innovations(id) ON DELETE CASCADE,\n"
        "    tagline text,\n"
        "    program text,\n"
        "    problem text,\n"
        "    target_group text,\n"
        "    who_can_use text,\n"
        "    effectiveness text,\n"
        "    authors text[] NOT NULL DEFAULT '{}',\n"
        "    -- file names inside backend/seed_media/<innovation_id>/\n"
        "    photos text[] NOT NULL DEFAULT '{}',\n"
        "    license_name text,\n"
        "    license_url text,\n"
        "    source_url text,\n"
        "    created_at timestamptz NOT NULL DEFAULT now(),\n"
        "    updated_at timestamptz NOT NULL DEFAULT now()\n"
        ");\n\n"
        "-- rows generated by media/build_app_seed.py from media/innovations.json; do not edit by hand\n"
        "INSERT INTO innovation_profiles (\n"
        "    innovation_id, tagline, program, problem, target_group, who_can_use, effectiveness,\n"
        "    authors, photos, license_name, license_url, source_url\n)\nVALUES\n"
        + ",\n".join(profiles)
        + "\nON CONFLICT (innovation_id) DO NOTHING;\n",
        encoding="utf-8",
    )
    print(f"seed media: {total / 2**20:.1f} MB", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())

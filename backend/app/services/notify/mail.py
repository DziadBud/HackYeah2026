import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Protocol

from jinja2 import Environment, FileSystemLoader, StrictUndefined, select_autoescape


@dataclass(frozen=True)
class Mail:
    # one layout for every notification; the notifier only fills these fields
    subject: str
    heading: str
    intro: str
    cta_label: str
    cta_url: str
    preheader: str = ""
    badge: str = ""
    quote_label: str = ""
    quote: str = ""
    reply: str = ""
    details: tuple[tuple[str, str], ...] = ()
    steps: tuple[str, ...] = ()


@dataclass(frozen=True)
class Rendered:
    subject: str
    text: str
    html: str


_env = Environment(
    loader=FileSystemLoader(Path(__file__).parent / "templates"),
    # user text ends up in the html, so escaping is a security need
    autoescape=select_autoescape(["html"]),
    undefined=StrictUndefined,
    trim_blocks=True,
    lstrip_blocks=True,
)


def render(mail: Mail, web_url: str, redirected: bool) -> Rendered:
    ctx = {"m": mail, "web_url": web_url, "redirected": redirected}
    return Rendered(
        subject=mail.subject,
        text=_env.get_template("mail.txt").render(ctx),
        html=_env.get_template("mail.html").render(ctx),
    )


class Mailer(Protocol):
    def send(self, to: str, mail: Rendered) -> None: ...


class SmtpMailer:
    # with credentials: starttls + login (gmail on 587); without: plain smtp (mailpit)
    def __init__(
        self,
        host: str,
        port: int,
        sender: str,
        username: str = "",
        password: str = "",
        timeout: float = 10,
    ) -> None:
        self._host = host
        self._port = port
        self._sender = sender
        self._username = username
        self._password = password
        self._timeout = timeout

    def send(self, to: str, mail: Rendered) -> None:
        msg = EmailMessage()
        msg["From"] = f"Hub Innowacji Społecznych <{self._sender}>"
        msg["To"] = to
        msg["Subject"] = mail.subject
        msg.set_content(mail.text)
        msg.add_alternative(mail.html, subtype="html")
        with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as smtp:
            if self._username:
                smtp.starttls()
                smtp.login(self._username, self._password)
            smtp.send_message(msg)


def build_mailer(
    host: str, port: int, sender: str, username: str = "", password: str = ""
) -> Mailer | None:
    # no smtp host or sender = notifications off (tests, local runs without mail config)
    return SmtpMailer(host, port, sender, username, password) if host and sender else None

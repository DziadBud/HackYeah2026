import logging
import smtplib
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

logger = logging.getLogger(__name__)

SMTP_TIMEOUT_SECONDS = 10


@dataclass(frozen=True)
class Mail:
    to: str
    subject: str
    body: str


class Notifier(Protocol):
    def send(self, mail: Mail) -> None: ...


class SmtpNotifier:
    # gmail: smtp.gmail.com:587, starttls, app password as smtp_password
    def __init__(self, host: str, port: int, username: str, password: str, sender: str) -> None:
        self._host = host
        self._port = port
        self._username = username
        self._password = password
        self._sender = sender

    def send(self, mail: Mail) -> None:
        msg = EmailMessage()
        msg["From"] = self._sender
        msg["To"] = mail.to
        msg["Subject"] = mail.subject
        msg.set_content(mail.body)
        with smtplib.SMTP(self._host, self._port, timeout=SMTP_TIMEOUT_SECONDS) as smtp:
            smtp.starttls()
            if self._username:
                smtp.login(self._username, self._password)
            smtp.send_message(msg)


class LogNotifier:
    """used when smtp is not configured: the mail only goes to the log"""

    def send(self, mail: Mail) -> None:
        logger.info("mail (smtp not configured) to=%s subject=%s", mail.to, mail.subject)


class RedirectNotifier:
    """testing safety net: every mail goes to one inbox, the real recipient is kept in the text"""

    def __init__(self, inner: Notifier, to: str) -> None:
        self._inner = inner
        self._to = to

    def send(self, mail: Mail) -> None:
        self._inner.send(
            Mail(
                to=self._to,
                subject=f"[test → {mail.to}] {mail.subject}",
                body=f"(test: ta wiadomość trafiłaby do {mail.to})\n\n{mail.body}",
            )
        )


class BackgroundNotifier:
    """at-most-once: sent off the request thread, a failure is logged and not retried.
    the db status stays the source of truth and the admin inbox still lists everything."""

    def __init__(self, inner: Notifier) -> None:
        self._inner = inner
        # one worker keeps the smtp server from seeing a burst of parallel logins
        self._pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix="mail")

    def send(self, mail: Mail) -> None:
        self._pool.submit(self._send, mail)

    def _send(self, mail: Mail) -> None:
        try:
            self._inner.send(mail)
        except Exception:
            logger.exception("mail to %s failed: %s", mail.to, mail.subject)

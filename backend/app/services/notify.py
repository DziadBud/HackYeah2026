# R10/R12: email notifications to the ROPS admin and to authors who left an email
# at-most-once: sent in a background task after the commit, a failed send is logged and dropped.
# the admin inbox stays the source of truth, so a lost mail delays a reply but loses no data
import logging
import smtplib
from collections.abc import Callable, Iterable
from email.message import EmailMessage
from typing import Any, Protocol

from fastapi import BackgroundTasks

from app.config import settings
from app.schemas.admin.ideas import IdeaStatus

logger = logging.getLogger(__name__)

IDEA_STATUS_LABELS = {
    IdeaStatus.NEW: "nowy",
    IdeaStatus.IN_REVIEW: "w ocenie",
    IdeaStatus.ACCEPTED: "przyjęty",
    IdeaStatus.REJECTED: "odrzucony",
}


class Mailer(Protocol):
    def send(self, to: str, subject: str, body: str) -> None: ...


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

    def send(self, to: str, subject: str, body: str) -> None:
        msg = EmailMessage()
        msg["From"] = self._sender
        msg["To"] = to
        msg["Subject"] = subject
        msg.set_content(body)
        with smtplib.SMTP(self._host, self._port, timeout=self._timeout) as smtp:
            if self._username:
                smtp.starttls()
                smtp.login(self._username, self._password)
            smtp.send_message(msg)


Schedule = Callable[..., Any]


class Notifier:
    # schedule is BackgroundTasks.add_task in the app, so mails go out after the response
    def __init__(
        self,
        mailer: Mailer | None,
        schedule: Schedule,
        admin_email: str,
        web_url: str,
        redirect_to: str = "",
    ) -> None:
        self._mailer = mailer
        self._schedule = schedule
        self._admin_email = admin_email
        self._web_url = web_url.rstrip("/")
        self._redirect_to = redirect_to

    def _send(self, to: str | None, subject: str, body: str) -> None:
        # testing: every mail goes to one inbox, even when the author left no email,
        # so the whole reply path can be checked before the frontend collects emails
        if self._redirect_to:
            to = self._redirect_to
        if self._mailer is None or not to:
            return
        self._schedule(self._deliver, to, subject, body)

    def _deliver(self, to: str, subject: str, body: str) -> None:
        assert self._mailer is not None
        try:
            self._mailer.send(to, subject, body)
        except Exception:
            # no address in the log: it is personal data
            logger.exception("notification not sent: %s", subject)

    def _admin(self, subject: str, body: str) -> None:
        self._send(self._admin_email, subject, f"{body}\n\nPanel administratora: {self._web_url}/admin")

    def _innovation_url(self, innovation_id: str) -> str:
        return f"{self._web_url}/innowacje/{innovation_id}"

    # to the admin

    def new_idea(self, idea_id: str, summary: str) -> None:
        self._admin("Nowy pomysł do oceny", f"Wpłynął nowy pomysł ({idea_id}):\n\n{summary}")

    def new_problem_report(self, problem_report_id: str, text: str) -> None:
        self._admin(
            "Nowe zgłoszenie problemu z prośbą o kontakt",
            f"Autor zgłoszenia ({problem_report_id}) zostawił e-mail i czeka na odpowiedź:\n\n{text}",
        )

    def new_thread(self, innovation_id: str, title: str) -> None:
        self._admin(
            "Nowy wątek czeka na moderację",
            f"Wątek „{title}” przy innowacji {innovation_id} czeka na publikację.",
        )

    def new_thread_reply(self, thread_title: str) -> None:
        self._admin(
            "Nowa odpowiedź czeka na moderację",
            f"Odpowiedź w wątku „{thread_title}” czeka na publikację.",
        )

    # to authors

    def idea_replied(self, email: str | None, summary: str, reply: str) -> None:
        self._send(
            email,
            "Odpowiedź ROPS na Twój pomysł",
            f"Twój pomysł:\n{summary}\n\nOdpowiedź koordynatora ROPS:\n{reply}",
        )

    def idea_status_changed(self, email: str | None, summary: str, status: IdeaStatus) -> None:
        self._send(
            email,
            f"Twój pomysł ma nowy status: {IDEA_STATUS_LABELS[status]}",
            f"Twój pomysł:\n{summary}\n\nNowy status: {IDEA_STATUS_LABELS[status]}.",
        )

    def problem_report_replied(self, email: str | None, text: str, reply: str) -> None:
        self._send(
            email,
            "Odpowiedź ROPS na Twoje zgłoszenie",
            f"Twoje zgłoszenie:\n{text}\n\nOdpowiedź koordynatora ROPS:\n{reply}",
        )

    def thread_published(self, email: str | None, innovation_id: str, title: str) -> None:
        self._send(
            email,
            "Twój wątek został opublikowany",
            f"Wątek „{title}” jest już widoczny: {self._innovation_url(innovation_id)}",
        )

    def reply_published(
        self, reply_email: str | None, thread_email: str | None, innovation_id: str, title: str
    ) -> None:
        url = self._innovation_url(innovation_id)
        self._send(reply_email, "Twoja odpowiedź została opublikowana", f"Odpowiedź w wątku „{title}”: {url}")
        if thread_email != reply_email:
            self._send(thread_email, "Nowa odpowiedź w Twoim wątku", f"Ktoś odpowiedział w wątku „{title}”: {url}")

    def grant_call_opened(self, emails: Iterable[str], name: str, deadline: str) -> None:
        # one mail per author, so addresses are never shared between recipients
        for email in [self._redirect_to] if self._redirect_to else emails:
            self._send(
                email,
                f"Otwarty nabór: {name}",
                f"ROPS otworzył nabór „{name}” (termin: {deadline}).\n"
                f"Możesz przygotować wniosek na podstawie swojego pomysłu: {self._web_url}",
            )


def build_mailer(
    host: str, port: int, sender: str, username: str = "", password: str = ""
) -> Mailer | None:
    # no smtp host or sender = notifications off (tests, local runs without mail config)
    return SmtpMailer(host, port, sender, username, password) if host and sender else None


_mailer = build_mailer(
    settings.smtp_host,
    settings.smtp_port,
    settings.mail_from,
    settings.smtp_username,
    settings.smtp_password,
)


def get_notifier(background: BackgroundTasks) -> Notifier:
    return Notifier(
        _mailer,
        background.add_task,
        settings.admin_notify_email,
        settings.web_url,
        settings.mail_redirect_to,
    )

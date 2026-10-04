# R10/R12: email notifications to users who left their own email (consent given on the item).
# the admin gets no mail: new items wait in the admin inbox (GET /admin/inbox)
# at-most-once: sent in a background task after the commit, a failed send is logged and dropped.
# the admin inbox stays the source of truth, so a lost mail delays a reply but loses no data
import logging
from collections.abc import Callable, Iterable
from datetime import date
from typing import Any
from urllib.parse import urlencode

from fastapi import BackgroundTasks

from app.config import settings
from app.schemas.admin.ideas import IdeaStatus
from app.schemas.admin.test_signups import TestSignupStatus
from app.schemas.public.grant_applications import GrantApplicationStatus
from app.services.notify.mail import Mail, Mailer, Rendered, SmtpMailer, build_mailer, render

__all__ = ["Mail", "Mailer", "Notifier", "Rendered", "SmtpMailer", "build_mailer", "get_notifier"]

logger = logging.getLogger(__name__)

# community section on the innovation page (frontend Community.tsx)
COMMUNITY_ANCHOR = "community-heading"

Schedule = Callable[..., Any]


def _short(text: str, limit: int = 60) -> str:
    text = " ".join(text.split())
    return text if len(text) <= limit else text[: limit - 1].rstrip() + "…"


class Notifier:
    # schedule is BackgroundTasks.add_task in the app, so mails go out after the response
    def __init__(
        self,
        mailer: Mailer | None,
        schedule: Schedule,
        web_url: str,
        redirect_to: str = "",
        api_url: str = "",
    ) -> None:
        self._mailer = mailer
        self._schedule = schedule
        self._web_url = web_url.rstrip("/")
        self._redirect_to = redirect_to
        self._api_url = api_url.rstrip("/")

    def _send(self, to: str | None, mail: Mail) -> None:
        # only people who gave their own address get mail
        if self._mailer is None or not to:
            return
        # testing: real recipients are swapped for one inbox
        if self._redirect_to:
            to = self._redirect_to
        # rendered here, not in the task: a template error fails the request's tests, not silently later
        rendered = render(mail, self._web_url, redirected=bool(self._redirect_to))
        self._schedule(self._deliver, to, rendered)

    def _deliver(self, to: str, mail: Rendered) -> None:
        assert self._mailer is not None
        try:
            self._mailer.send(to, mail)
        except Exception:
            # no address in the log: it is personal data
            logger.exception("notification not sent: %s", mail.subject)

    def _url(self, path: str, **query: str) -> str:
        return f"{self._web_url}{path}" + (f"?{urlencode(query)}" if query else "")

    def _innovation_url(self, innovation_id: str, anchor: str) -> str:
        return f"{self._url(f'/innowacje/{innovation_id}')}#{anchor}"

    def idea_replied(self, email: str | None, summary: str, reply: str) -> None:
        self._send(
            email,
            Mail(
                subject="Mamy odpowiedź w sprawie Twojej propozycji",
                preheader=_short(reply, 120),
                heading="Dzięki, że chcesz coś zmienić!",
                intro="Zespół Hubu przyjrzał się Twojej propozycji i przesyła odpowiedź.",
                quote_label="Twoja propozycja",
                quote=summary,
                reply=reply,
                cta_label="Zobacz, co działa w innych gminach",
                cta_url=self._url("/innowacje"),
            ),
        )

    def idea_status_changed(self, email: str | None, summary: str, status: IdeaStatus) -> None:
        # in_review is an internal step; only a decision is worth a mail
        if status == IdeaStatus.ACCEPTED:
            mail = Mail(
                subject="Dobra wiadomość: Twoja propozycja przechodzi dalej",
                badge="Przyjęta",
                heading="Twoja propozycja przechodzi dalej!",
                intro="Zespół Hubu chce ją rozwijać razem z Tobą.",
                quote_label="Twoja propozycja",
                quote=summary,
                steps=(
                    "Wkrótce się odezwiemy, żeby umówić rozmowę.",
                    "Gdy ruszy nabór grantowy, damy znać i pomożemy przygotować wniosek.",
                ),
                cta_label="Poszukaj inspiracji",
                cta_url=self._url("/innowacje"),
            )
        elif status == IdeaStatus.REJECTED:
            mail = Mail(
                subject="Odpowiedź w sprawie Twojej propozycji",
                heading="Tym razem nie możemy jej rozwinąć",
                intro=(
                    "Dziękujemy za zaangażowanie. Często podobny problem rozwiązuje już sprawdzona "
                    "innowacja – może któraś przyda się w Twojej okolicy."
                ),
                quote_label="Twoja propozycja",
                quote=summary,
                cta_label="Przeglądaj innowacje",
                cta_url=self._url("/innowacje"),
            )
        else:
            return
        self._send(email, mail)

    def problem_report_replied(self, email: str | None, text: str, reply: str) -> None:
        self._send(
            email,
            Mail(
                subject="Mamy odpowiedź na Twoje zgłoszenie",
                preheader=_short(reply, 120),
                heading="Mamy odpowiedź na Twoje zgłoszenie",
                intro="Tę samą odpowiedź zobaczą osoby, które zgłosiły podobny problem.",
                quote_label="Twoje zgłoszenie",
                quote=text,
                reply=reply,
                cta_label="Szukaj kolejnych rozwiązań",
                cta_url=self._url("/"),
            ),
        )

    def thread_published(self, email: str | None, innovation_id: str, title: str) -> None:
        self._send(
            email,
            Mail(
                subject="Twoje pytanie jest już widoczne",
                heading="Twoje pytanie jest już w społeczności",
                intro="Inni praktycy i eksperci mogą teraz odpowiadać. Napiszemy, gdy ktoś się odezwie.",
                quote_label="Pytanie",
                quote=title,
                cta_label="Zobacz dyskusję",
                cta_url=self._innovation_url(innovation_id, COMMUNITY_ANCHOR),
            ),
        )

    def reply_published(
        self, reply_email: str | None, thread_email: str | None, innovation_id: str, title: str
    ) -> None:
        url = self._innovation_url(innovation_id, COMMUNITY_ANCHOR)
        self._send(
            reply_email,
            Mail(
                subject="Twoja odpowiedź jest już widoczna",
                heading="Dziękujemy za podzielenie się doświadczeniem",
                intro=f"Twoja odpowiedź w dyskusji „{title}” jest już widoczna dla wszystkich.",
                cta_label="Zobacz dyskusję",
                cta_url=url,
            ),
        )
        if thread_email != reply_email:
            self._send(
                thread_email,
                Mail(
                    subject="Ktoś odpowiedział na Twoje pytanie",
                        heading="Ktoś odpowiedział na Twoje pytanie",
                    intro=f"W dyskusji „{title}” pojawiła się nowa odpowiedź.",
                    cta_label="Przeczytaj",
                    cta_url=url,
                ),
            )

    def grant_call_opened(
        self, emails: Iterable[str], name: str, deadline: date, sections: list[str]
    ) -> None:
        details = (("Termin", deadline.strftime("%d.%m.%Y")),)
        if sections:
            details += (("We wniosku opiszesz", ", ".join(sections)),)
        mail = Mail(
            subject=f"Ruszył nabór „{name}”",
            badge="Nabór otwarty",
            heading=f"Ruszył nabór „{name}”",
            intro=(
                "Jeśli Twoja propozycja wciąż czeka na realizację, to dobry moment na wniosek. "
                "Pomożemy go przygotować – generator działa tylko w czasie naboru."
            ),
            details=details,
            cta_label="Przygotuj wniosek",
            cta_url=self._url("/", wniosek="1"),
        )
        # one mail per author, so addresses are never shared between recipients
        recipients = list(emails)
        # testing: one copy is enough when everything goes to the same inbox
        for email in recipients[:1] if self._redirect_to else recipients:
            self._send(email, mail)

    def test_signup_status(
        self,
        email: str,
        signup_id: str,
        innovation_title: str,
        status: TestSignupStatus,
    ) -> None:
        if status == TestSignupStatus.ACCEPTED:
            mail = Mail(
                subject=f"Zapraszamy do testów: {innovation_title}",
                badge="Jesteś w testach",
                heading=f"Zapraszamy Cię do testów „{innovation_title}”",
                intro="Super, że chcesz sprawdzić to rozwiązanie u siebie.",
                steps=(
                    "Wypróbuj rozwiązanie w swojej gminie lub organizacji. W razie pytań zespół Hubu pomoże.",
                    "Po teście oceń je – wystarczy przycisk poniżej. Warto zachować tę wiadomość.",
                ),
                cta_label="Oceń rozwiązanie",
                cta_url=self._rating_url(signup_id),
            )
        elif status == TestSignupStatus.COMPLETED:
            mail = Mail(
                subject=f"Jak sprawdził się „{innovation_title}”?",
                heading=f"Jak sprawdził się „{innovation_title}”?",
                intro="Dziękujemy za testy! Twoja ocena pomoże innym gminom wybrać dobre rozwiązanie. To zajmie chwilę.",
                cta_label="Oceń rozwiązanie",
                cta_url=self._rating_url(signup_id),
            )
        elif status == TestSignupStatus.REJECTED:
            mail = Mail(
                subject=f"Testy „{innovation_title}”",
                heading="Tym razem zabrakło miejsc w testach",
                intro=(
                    f"Dziękujemy za chęć przetestowania „{innovation_title}”. Liczba miejsc była "
                    "ograniczona, ale inne innowacje też szukają testerów."
                ),
                cta_label="Zobacz inne innowacje",
                cta_url=self._url("/innowacje"),
            )
        else:
            return
        self._send(email, mail)

    def grant_application_decided(
        self, email: str | None, title: str, status: GrantApplicationStatus, message: str | None
    ) -> None:
        title = title.strip() or "Twój wniosek"
        if status == GrantApplicationStatus.ACCEPTED:
            mail = Mail(
                subject=f"Twój wniosek grantowy został przyjęty: {_short(title)}",
                badge="Przyjęty",
                heading="Gratulacje, Twój wniosek został przyjęty!",
                intro="Zespół Hubu zapoznał się z wnioskiem i chce wesprzeć Twoją innowację.",
                quote_label="Twój wniosek",
                quote=title,
                reply=message or "",
                steps=(
                    "Wkrótce się odezwiemy, żeby omówić umowę i kolejne kroki.",
                    "Zachowaj tę wiadomość – przyda się przy rozmowie.",
                ),
                cta_label="Zobacz inne innowacje",
                cta_url=self._url("/innowacje"),
            )
        elif status == GrantApplicationStatus.REJECTED:
            mail = Mail(
                subject=f"Odpowiedź w sprawie wniosku: {_short(title)}",
                heading="Tym razem nie możemy przyznać grantu",
                intro=(
                    "Dziękujemy za przygotowanie wniosku. Możesz złożyć nowy w kolejnym naborze – "
                    "warto też zobaczyć, jak podobne problemy rozwiązano w innych gminach."
                ),
                quote_label="Twój wniosek",
                quote=title,
                reply=message or "",
                cta_label="Przeglądaj innowacje",
                cta_url=self._url("/innowacje"),
            )
        else:
            return
        self._send(email, mail)

    def _rating_url(self, signup_id: str) -> str:
        # the signup id is the tester's token; it lives only inside the link.
        # the api serves the rating page itself, so it works without the frontend
        return f"{self._api_url}/ratings/{signup_id}"


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
        settings.web_url,
        settings.mail_redirect_to,
        settings.api_url,
    )

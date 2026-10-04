# R10/R12: email notifications to the ROPS admin and to authors who left an email
# at-most-once: sent in a background task after the commit, a failed send is logged and dropped.
# the admin inbox stays the source of truth, so a lost mail delays a reply but loses no data
import logging
from collections.abc import Callable, Iterable
from datetime import date
from typing import Any
from urllib.parse import urlencode

from fastapi import BackgroundTasks

from app.config import settings
from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.ideas import IdeaStage, IdeaStatus
from app.schemas.admin.test_signups import TestSignupStatus
from app.services.notify.mail import Mail, Mailer, Rendered, SmtpMailer, build_mailer, render

__all__ = ["Mail", "Mailer", "Notifier", "Rendered", "SmtpMailer", "build_mailer", "get_notifier"]

logger = logging.getLogger(__name__)

STAGE_LABELS = {
    IdeaStage.CONCEPT: "pomysł na papierze",
    IdeaStage.PROTOTYPE: "prototyp",
    IdeaStage.PILOT: "pilotaż",
    IdeaStage.RUNNING: "już działa",
}
AREA_LABELS = {
    ChallengeArea.FOSTER_CARE: "Rodzina i piecza zastępcza",
    ChallengeArea.HOMELESSNESS: "Bezdomność",
    ChallengeArea.DISABILITY: "Niepełnosprawność",
    ChallengeArea.POVERTY: "Ubóstwo",
    ChallengeArea.FOREIGNERS: "Integracja cudzoziemców",
    ChallengeArea.HEALTH: "Zdrowie",
    ChallengeArea.MENTAL_HEALTH: "Zdrowie psychiczne",
    ChallengeArea.SENIORS: "Seniorzy",
}
# community section on the innovation page (frontend Community.tsx)
COMMUNITY_ANCHOR = "community-heading"
# rating form on the innovation page (frontend FE-02)
RATING_ANCHOR = "ocena"

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
        admin_email: str,
        web_url: str,
        redirect_to: str = "",
    ) -> None:
        self._mailer = mailer
        self._schedule = schedule
        self._admin_email = admin_email
        self._web_url = web_url.rstrip("/")
        self._redirect_to = redirect_to

    def _send(self, to: str | None, mail: Mail) -> None:
        # testing: every mail goes to one inbox, even when the author left no email,
        # so the whole reply path can be checked before the frontend collects emails
        if self._redirect_to:
            to = self._redirect_to
        if self._mailer is None or not to:
            return
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

    def _innovation_url(self, innovation_id: str, anchor: str = "", **query: str) -> str:
        url = self._url(f"/innowacje/{innovation_id}", **query)
        return f"{url}#{anchor}" if anchor else url

    # to the admin

    def new_idea(
        self, idea_id: str, summary: str, essence: str, target_group: str, stage: IdeaStage
    ) -> None:
        self._send(
            self._admin_email,
            Mail(
                subject=f"Nowa propozycja: {_short(summary)}",
                audience="admin",
                preheader=_short(essence, 120),
                heading="Ktoś chce coś zmienić w swojej okolicy",
                intro="Przez Kreator pomysłów przyszła nowa propozycja. Autor czeka na Twoją odpowiedź.",
                quote_label="Propozycja",
                quote=f"{summary}\n\n{essence}",
                details=(("Dla kogo", target_group), ("Na jakim etapie", STAGE_LABELS[stage])),
                cta_label="Przejrzyj i odpowiedz",
                cta_url=self._url("/admin"),
            ),
        )

    def new_problem_report(
        self, problem_report_id: str, text: str, city: str, area: ChallengeArea | None
    ) -> None:
        details = tuple(
            (label, value)
            for label, value in (("Skąd", city), ("Obszar", AREA_LABELS[area] if area else ""))
            if value
        )
        self._send(
            self._admin_email,
            Mail(
                subject=f"Ktoś czeka na kontakt: {_short(text)}",
                audience="admin",
                preheader=_short(text, 120),
                heading="Mieszkaniec opisał problem i prosi o kontakt",
                intro="Twoja odpowiedź z panelu trafi do niego e-mailem.",
                quote_label="Opis problemu",
                quote=text,
                details=details,
                cta_label="Odpowiedz",
                cta_url=self._url("/admin/zgloszenia"),
            ),
        )

    def new_thread(self, innovation_id: str, innovation_title: str, title: str, body: str) -> None:
        self._send(
            self._admin_email,
            Mail(
                subject=f"Nowe pytanie w społeczności: {_short(title)}",
                audience="admin",
                heading="Nowe pytanie czeka na publikację",
                intro=f"Dotyczy innowacji „{innovation_title}”. Po publikacji zobaczą je wszyscy odwiedzający.",
                quote_label=title,
                quote=body,
                cta_label="Opublikuj lub ukryj",
                cta_url=self._url("/admin"),
            ),
        )

    def new_thread_reply(self, thread_title: str, body: str) -> None:
        self._send(
            self._admin_email,
            Mail(
                subject=f"Nowa odpowiedź do sprawdzenia: {_short(thread_title)}",
                audience="admin",
                heading="Ktoś odpowiedział w dyskusji",
                intro=f"Dyskusja: „{thread_title}”. Odpowiedź pojawi się na stronie po Twojej akceptacji.",
                quote=body,
                quote_label="Odpowiedź",
                cta_label="Sprawdź odpowiedź",
                cta_url=self._url("/admin"),
            ),
        )

    def new_test_signups(self, problem_text: str, innovation_titles: list[str]) -> None:
        self._send(
            self._admin_email,
            Mail(
                subject=f"Chętny do testów: {_short(', '.join(innovation_titles))}",
                audience="admin",
                heading="Ktoś chce przetestować rozwiązanie u siebie",
                intro="Zgłoszenie przyszło razem z opisem problemu, z którym ta osoba się mierzy.",
                quote_label="Z czym się mierzy",
                quote=problem_text,
                details=tuple(("Chce testować", t) for t in innovation_titles),
                cta_label="Rozpatrz zgłoszenie",
                cta_url=self._url("/admin"),
            ),
        )

    # to authors

    def idea_replied(self, email: str | None, summary: str, reply: str) -> None:
        self._send(
            email,
            Mail(
                subject="Mamy odpowiedź w sprawie Twojej propozycji",
                audience="author",
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
                audience="author",
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
                audience="author",
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
                audience="author",
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
                audience="author",
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
                audience="author",
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
                    audience="author",
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
            audience="author",
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
        for email in [self._redirect_to] if self._redirect_to else emails:
            self._send(email, mail)

    def test_signup_status(
        self,
        email: str,
        signup_id: str,
        innovation_id: str,
        innovation_title: str,
        status: TestSignupStatus,
    ) -> None:
        # the signup id in the link is the tester's token for the rating form; it is never shown as text
        rate_url = self._innovation_url(innovation_id, RATING_ANCHOR, test_signup=signup_id)
        if status == TestSignupStatus.ACCEPTED:
            mail = Mail(
                subject=f"Zapraszamy do testów: {innovation_title}",
                audience="author",
                badge="Jesteś w testach",
                heading=f"Zapraszamy Cię do testów „{innovation_title}”",
                intro="Super, że chcesz sprawdzić to rozwiązanie u siebie.",
                steps=(
                    "Przeczytaj opis i materiały na stronie innowacji.",
                    "Wypróbuj rozwiązanie w swojej gminie lub organizacji. W razie pytań zespół Hubu pomoże.",
                    "Na koniec oceń, jak się sprawdziło – wystarczy wrócić na stronę z tej wiadomości.",
                ),
                cta_label="Przejdź do innowacji",
                cta_url=rate_url,
            )
        elif status == TestSignupStatus.COMPLETED:
            mail = Mail(
                subject=f"Jak sprawdził się „{innovation_title}”?",
                audience="author",
                heading=f"Jak sprawdził się „{innovation_title}”?",
                intro="Dziękujemy za testy! Twoja ocena pomoże innym gminom wybrać dobre rozwiązanie.",
                ratings=tuple(
                    (n, self._innovation_url(innovation_id, RATING_ANCHOR, test_signup=signup_id, rating=str(n)))
                    for n in range(5, 0, -1)
                ),
                cta_label="Dodaj opinię",
                cta_url=rate_url,
            )
        elif status == TestSignupStatus.REJECTED:
            mail = Mail(
                subject=f"Testy „{innovation_title}”",
                audience="author",
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

"""plain-language polish mails; every builder returns None when there is nobody to send to"""

from app.services.notify.notifier import Mail

SIGNATURE = "\n\n--\nMałopolski Hub Innowacji Społecznych (ROPS Kraków)\nTa wiadomość została wysłana automatycznie."


class Mails:
    def __init__(self, admin_email: str, web_url: str) -> None:
        self._admin = admin_email
        self._web = web_url.rstrip("/")

    def _to_admin(self, subject: str, body: str) -> Mail | None:
        if not self._admin:
            return None
        return Mail(self._admin, subject, f"{body}\n\nPanel: {self._web}/admin{SIGNATURE}")

    @staticmethod
    def _to(email: str | None, subject: str, body: str) -> Mail | None:
        return Mail(email, subject, body + SIGNATURE) if email else None

    # to the admin

    def new_idea(self, summary: str) -> Mail | None:
        return self._to_admin("Nowy pomysł do przejrzenia", f"Ktoś zgłosił nowy pomysł:\n\n{summary}")

    def new_thread(self, title: str, innovation_id: str) -> Mail | None:
        return self._to_admin(
            "Nowy wątek czeka na moderację",
            f"Nowy wątek przy innowacji {innovation_id}:\n\n{title}",
        )

    def new_reply(self, thread_title: str) -> Mail | None:
        return self._to_admin(
            "Nowa odpowiedź czeka na moderację", f"Nowa odpowiedź w wątku:\n\n{thread_title}"
        )

    def new_test_signups(self, innovation_titles: list[str]) -> Mail | None:
        listed = "\n".join(f"- {t}" for t in innovation_titles)
        return self._to_admin("Nowe zgłoszenie do testów", f"Ktoś chce przetestować:\n\n{listed}")

    # to the author

    def idea_reply(self, email: str | None, summary: str, message: str) -> Mail | None:
        return self._to(
            email, "ROPS odpowiedział na Twój pomysł", f"Twój pomysł:\n{summary}\n\nOdpowiedź ROPS:\n{message}"
        )

    def idea_status(self, email: str | None, summary: str, status_label: str) -> Mail | None:
        return self._to(
            email, "Zmiana statusu Twojego pomysłu", f"Twój pomysł:\n{summary}\n\nNowy status: {status_label}"
        )

    def problem_report_reply(self, email: str | None, text: str, message: str) -> Mail | None:
        return self._to(
            email,
            "ROPS odpowiedział na Twoje zgłoszenie",
            f"Twoje zgłoszenie:\n{text}\n\nOdpowiedź ROPS:\n{message}",
        )

    def thread_published(self, email: str | None, title: str, innovation_id: str) -> Mail | None:
        return self._to(
            email,
            "Twój wątek jest już widoczny",
            f"Opublikowaliśmy Twój wątek „{title}”.\n\n{self._web}/innovations/{innovation_id}",
        )

    def reply_published(self, email: str | None, innovation_id: str) -> Mail | None:
        return self._to(
            email,
            "Twoja odpowiedź jest już widoczna",
            f"Opublikowaliśmy Twoją odpowiedź.\n\n{self._web}/innovations/{innovation_id}",
        )

    def test_signup_status(
        self, email: str, signup_id: str, innovation_id: str, innovation_title: str, status: str
    ) -> Mail | None:
        if status == "accepted":
            # the signup id is unguessable, so the link works as the tester's token
            link = f"{self._web}/innovations/{innovation_id}?test_signup={signup_id}"
            body = (
                f"Zakwalifikowaliśmy Cię do testowania: {innovation_title}.\n"
                "Pracownik ROPS skontaktuje się z Tobą, żeby ustalić szczegóły.\n\n"
                f"Po teście oceń rozwiązanie i zaproponuj ulepszenia tutaj:\n{link}"
            )
            return self._to(email, "Zapraszamy do testowania innowacji", body)
        if status == "rejected":
            body = f"Dziękujemy za zgłoszenie do testów: {innovation_title}. Tym razem nie możemy Cię zaprosić."
            return self._to(email, "Zgłoszenie do testów", body)
        if status == "completed":
            body = f"Dziękujemy za udział w testach: {innovation_title}. Twoja opinia pomoże rozwinąć rozwiązanie."
            return self._to(email, "Dziękujemy za test", body)
        return None

    def grant_call_opened(self, email: str | None, call_name: str, deadline: str) -> Mail | None:
        return self._to(
            email,
            f"Otwarty nabór: {call_name}",
            f"Ruszył nabór „{call_name}” (termin: {deadline}).\n"
            f"Możesz przygotować wniosek na podstawie swojego pomysłu: {self._web}",
        )

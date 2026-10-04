import logging
from datetime import date

import pytest
from fastapi import BackgroundTasks

from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.ideas import IdeaStage, IdeaStatus
from app.schemas.admin import test_signups
from app.services.notify import Notifier, Rendered, SmtpMailer, build_mailer, mail as mail_module

ADMIN = "rops-admin@example.org"
AUTHOR = "author@example.org"
WEB = "http://web.test"


class FakeMailer:
    def __init__(self, fail: bool = False) -> None:
        self.sent: list[tuple[str, Rendered]] = []
        self.fail = fail

    def send(self, to: str, mail: Rendered) -> None:
        if self.fail:
            raise OSError("smtp down")
        self.sent.append((to, mail))


def run_now(fn, *args) -> None:
    fn(*args)


def make(mailer: FakeMailer | None = None, redirect_to: str = "") -> Notifier:
    return Notifier(mailer, run_now, ADMIN, WEB + "/", redirect_to)


def one(mailer: FakeMailer) -> tuple[str, Rendered]:
    [sent] = mailer.sent
    return sent


@pytest.mark.parametrize(
    ("call", "cta_url"),
    [
        pytest.param(
            lambda n: n.new_idea("idea-1", "Obiady dla seniorów", "Wspólne gotowanie", "seniorzy", IdeaStage.CONCEPT),
            f"{WEB}/admin",
            id="#1 - OK - new idea",
        ),
        pytest.param(
            lambda n: n.new_problem_report("pr-1", "Brak transportu", "Tarnów", ChallengeArea.SENIORS),
            f"{WEB}/admin/zgloszenia",
            id="#2 - OK - problem report",
        ),
        pytest.param(
            lambda n: n.new_thread("wibraap", "Wibraap", "Pytanie", "Treść"),
            f"{WEB}/admin",
            id="#3 - OK - new thread",
        ),
        pytest.param(lambda n: n.new_thread_reply("Pytanie", "Treść"), f"{WEB}/admin", id="#4 - OK - new reply"),
        pytest.param(
            lambda n: n.new_test_signups("Samotni seniorzy", ["Wibraap", "Paczka"]),
            f"{WEB}/admin",
            id="#5 - OK - test signups",
        ),
    ],
)
def test_admin_mails(call, cta_url) -> None:
    mailer = FakeMailer()
    call(make(mailer))
    to, mail = one(mailer)
    assert to == ADMIN
    assert cta_url in mail.html and cta_url in mail.text
    assert "panelu Hubu" in mail.text


def test_new_idea_content() -> None:
    mailer = FakeMailer()
    make(mailer).new_idea("idea-1", "Obiady dla seniorów", "Wspólne gotowanie", "seniorzy", IdeaStage.PILOT)
    _, mail = one(mailer)
    assert mail.subject == "Nowa propozycja: Obiady dla seniorów"
    assert "pilotaż" in mail.html and "seniorzy" in mail.html and "Wspólne gotowanie" in mail.text
    # admins get what helps them act, not internal ids
    assert "idea-1" not in mail.html and "idea-1" not in mail.text


@pytest.mark.parametrize(
    ("call", "cta_url"),
    [
        pytest.param(lambda n: n.idea_replied(AUTHOR, "Pomysł", "Dziękujemy"), f"{WEB}/innowacje", id="#1 - OK - idea reply"),
        pytest.param(
            lambda n: n.idea_status_changed(AUTHOR, "Pomysł", IdeaStatus.ACCEPTED), f"{WEB}/innowacje", id="#2 - OK - accepted"
        ),
        pytest.param(
            lambda n: n.idea_status_changed(AUTHOR, "Pomysł", IdeaStatus.REJECTED), f"{WEB}/innowacje", id="#3 - OK - rejected"
        ),
        pytest.param(lambda n: n.problem_report_replied(AUTHOR, "Problem", "Odpowiedź"), f"{WEB}/", id="#4 - OK - report reply"),
        pytest.param(
            lambda n: n.thread_published(AUTHOR, "wibraap", "Pytanie"),
            f"{WEB}/innowacje/wibraap#community-heading",
            id="#5 - OK - thread published",
        ),
    ],
)
def test_author_mails(call, cta_url) -> None:
    mailer = FakeMailer()
    call(make(mailer))
    to, mail = one(mailer)
    assert to == AUTHOR
    assert cta_url in mail.html
    # the coordinator's address is never shown to users
    assert ADMIN not in mail.html and ADMIN not in mail.text


def test_reply_highlighted() -> None:
    mailer = FakeMailer()
    make(mailer).idea_replied(AUTHOR, "Obiady dla seniorów", "Zapraszamy na rozmowę")
    _, mail = one(mailer)
    assert mail.subject == "Mamy odpowiedź w sprawie Twojej propozycji"
    assert "Odpowiedź zespołu Hubu" in mail.html and "Zapraszamy na rozmowę" in mail.html


def test_in_review_sends_nothing() -> None:
    mailer = FakeMailer()
    make(mailer).idea_status_changed(AUTHOR, "Pomysł", IdeaStatus.IN_REVIEW)
    assert mailer.sent == []


def test_user_text_is_escaped_in_html() -> None:
    mailer = FakeMailer()
    make(mailer).idea_replied(AUTHOR, "<script>alert(1)</script>", "<b>x</b>")
    _, mail = one(mailer)
    assert "<script>" not in mail.html and "&lt;script&gt;" in mail.html
    assert "<b>x</b>" not in mail.html
    # plain text stays as typed
    assert "<script>alert(1)</script>" in mail.text


@pytest.mark.parametrize(
    ("reply_email", "thread_email", "expected"),
    [
        ("r@example.org", "t@example.org", ["r@example.org", "t@example.org"]),
        ("same@example.org", "same@example.org", ["same@example.org"]),
        (None, "t@example.org", ["t@example.org"]),
        (None, None, []),
    ],
    ids=["#1 - OK - both", "#2 - OK - same author once", "#3 - OK - thread only", "#4 - OK - nobody"],
)
def test_reply_published(reply_email, thread_email, expected) -> None:
    mailer = FakeMailer()
    make(mailer).reply_published(reply_email, thread_email, "wibraap", "Pytanie")
    assert [to for to, _ in mailer.sent] == expected


def test_grant_call_opened_one_mail_per_author() -> None:
    mailer = FakeMailer()
    make(mailer).grant_call_opened(["a@example.org", "b@example.org"], "Nabór 2026", date(2026, 12, 15), ["Opis", "Budżet"])
    assert [to for to, _ in mailer.sent] == ["a@example.org", "b@example.org"]
    _, mail = mailer.sent[0]
    assert "15.12.2026" in mail.html and "Opis, Budżet" in mail.html
    assert f"{WEB}/?wniosek=1" in mail.html


def test_test_signup_accepted_links_rating_form() -> None:
    mailer = FakeMailer()
    make(mailer).test_signup_status(AUTHOR, "sig-1", "wibraap", "Wibraap", test_signups.TestSignupStatus.ACCEPTED)
    _, mail = one(mailer)
    assert f'href="{WEB}/innowacje/wibraap?test_signup=sig-1#ocena"' in mail.html
    # the signup id is the rating token: only inside links, never as visible text
    assert mail.html.count("sig-1") == mail.html.count("test_signup=sig-1")


def test_test_signup_completed_has_five_rating_links() -> None:
    mailer = FakeMailer()
    make(mailer).test_signup_status(AUTHOR, "sig-1", "wibraap", "Wibraap", test_signups.TestSignupStatus.COMPLETED)
    _, mail = one(mailer)
    for n in range(1, 6):
        url = f"{WEB}/innowacje/wibraap?test_signup=sig-1&amp;rating={n}#ocena"
        assert url in mail.html
        assert url.replace("&amp;", "&") in mail.text
    assert "Bardzo dobrze" in mail.html


def test_test_signup_rejected() -> None:
    mailer = FakeMailer()
    make(mailer).test_signup_status(AUTHOR, "sig-1", "wibraap", "Wibraap", test_signups.TestSignupStatus.REJECTED)
    _, mail = one(mailer)
    assert "rating=" not in mail.html


def test_no_email_no_mail() -> None:
    mailer = FakeMailer()
    make(mailer).idea_replied(None, "Pomysł", "Dziękujemy")
    assert mailer.sent == []


def test_disabled_without_mailer() -> None:
    scheduled = []
    Notifier(None, lambda *a: scheduled.append(a), ADMIN, WEB).new_idea("i", "x", "y", "z", IdeaStage.CONCEPT)
    assert scheduled == []


def test_no_admin_email_no_mail() -> None:
    mailer = FakeMailer()
    Notifier(mailer, run_now, "", WEB).new_idea("i", "x", "y", "z", IdeaStage.CONCEPT)
    assert mailer.sent == []


def test_redirect_sends_everything_to_one_inbox() -> None:
    mailer = FakeMailer()
    n = make(mailer, redirect_to="test@example.org")
    n.new_idea("i", "x", "y", "z", IdeaStage.CONCEPT)
    n.idea_replied(AUTHOR, "Pomysł", "Dziękujemy")
    # no author email: still sent, so the reply path is testable
    n.problem_report_replied(None, "Problem", "Odpowiedź")
    n.grant_call_opened(["a@example.org", "b@example.org"], "Nabór", date(2026, 12, 15), [])
    n.grant_call_opened([], "Nabór", date(2026, 12, 15), [])
    assert [to for to, _ in mailer.sent] == ["test@example.org"] * 5
    assert "Tryb testowy: ta wiadomość trafiłaby do koordynatora ROPS" in mailer.sent[0][1].html
    assert "trafiłaby do autora zgłoszenia" in mailer.sent[1][1].html


def test_failed_send_is_logged_not_raised(caplog) -> None:
    with caplog.at_level(logging.ERROR):
        make(FakeMailer(fail=True)).idea_replied(AUTHOR, "Pomysł", "x")
    assert "notification not sent" in caplog.text
    # personal data stays out of the log
    assert AUTHOR not in caplog.text


def test_sends_after_response_via_background_tasks() -> None:
    mailer = FakeMailer()
    background = BackgroundTasks()
    Notifier(mailer, background.add_task, ADMIN, WEB).new_idea("i", "x", "y", "z", IdeaStage.CONCEPT)
    assert mailer.sent == []
    assert len(background.tasks) == 1


class FakeSmtp:
    calls: list = []

    def __init__(self, host, port, timeout):
        FakeSmtp.calls = [("connect", host, port)]

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        FakeSmtp.calls.append(("starttls",))

    def login(self, user, password):
        FakeSmtp.calls.append(("login", user, password))

    def send_message(self, msg):
        FakeSmtp.calls.append(("send", msg))


RENDERED = Rendered(subject="Temat", text="Treść", html="<p>Treść</p>")


def test_smtp_mailer_multipart(monkeypatch) -> None:
    monkeypatch.setattr(mail_module.smtplib, "SMTP", FakeSmtp)
    SmtpMailer("mailpit", 1025, "hub@example.org").send(AUTHOR, RENDERED)
    connect, (_, msg) = FakeSmtp.calls
    assert connect == ("connect", "mailpit", 1025)
    assert msg["To"] == AUTHOR and msg["Subject"] == "Temat" and msg["Reply-To"] is None
    assert "hub@example.org" in msg["From"]
    assert msg.get_body(("plain",)).get_content().strip() == "Treść"
    assert msg.get_body(("html",)).get_content().strip() == "<p>Treść</p>"


def test_smtp_mailer_starttls_login(monkeypatch) -> None:
    monkeypatch.setattr(mail_module.smtplib, "SMTP", FakeSmtp)
    SmtpMailer("smtp.gmail.com", 587, "hub@example.org", "user@example.org", "secret").send(AUTHOR, RENDERED)
    assert [c[0] for c in FakeSmtp.calls] == ["connect", "starttls", "login", "send"]
    assert FakeSmtp.calls[2] == ("login", "user@example.org", "secret")


def test_build_mailer_off_without_host_or_sender() -> None:
    assert build_mailer("", 1025, "hub@example.org") is None
    assert build_mailer("mailpit", 1025, "") is None
    assert isinstance(build_mailer("mailpit", 1025, "hub@example.org"), SmtpMailer)

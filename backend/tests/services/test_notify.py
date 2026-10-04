import logging
from datetime import date

import pytest
from fastapi import BackgroundTasks

from app.schemas.admin.ideas import IdeaStatus
from app.schemas.admin import test_signups
from app.services.notify import Notifier, Rendered, SmtpMailer, build_mailer, mail as mail_module

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
    return Notifier(mailer, run_now, WEB + "/", redirect_to)


def one(mailer: FakeMailer) -> tuple[str, Rendered]:
    [sent] = mailer.sent
    return sent


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


API = "http://api.test"


@pytest.mark.parametrize(
    "status",
    [test_signups.TestSignupStatus.ACCEPTED, test_signups.TestSignupStatus.COMPLETED],
    ids=["#1 - OK - accepted", "#2 - OK - completed"],
)
def test_tester_mails_link_rating_page(status) -> None:
    mailer = FakeMailer()
    Notifier(mailer, run_now, WEB, api_url=API + "/").test_signup_status(AUTHOR, "sig-1", "Wibraap", status)
    _, mail = one(mailer)
    url = f"{API}/ratings/sig-1"
    # one button; the stars live on the rating page, not in the mail
    assert f'href="{url}"' in mail.html and url in mail.text
    assert "Oceń rozwiązanie" in mail.html
    assert "★" not in mail.html and "rating=" not in mail.html
    # the signup id is the rating token: only inside the link, never as visible text
    assert mail.html.count("sig-1") == 1


def test_test_signup_rejected() -> None:
    mailer = FakeMailer()
    make(mailer).test_signup_status(AUTHOR, "sig-1", "Wibraap", test_signups.TestSignupStatus.REJECTED)
    _, mail = one(mailer)
    assert "/ratings/" not in mail.html
    assert f"{WEB}/innowacje" in mail.html


def test_no_email_no_mail() -> None:
    mailer = FakeMailer()
    make(mailer).idea_replied(None, "Pomysł", "Dziękujemy")
    assert mailer.sent == []


def test_disabled_without_mailer() -> None:
    scheduled = []
    Notifier(None, lambda *a: scheduled.append(a), WEB).idea_replied(AUTHOR, "Pomysł", "x")
    assert scheduled == []


def test_redirect_swaps_recipient_only_for_users_with_email() -> None:
    mailer = FakeMailer()
    n = make(mailer, redirect_to="test@example.org")
    n.idea_replied(AUTHOR, "Pomysł", "Dziękujemy")
    # no email given: nothing is sent, also in test mode
    n.problem_report_replied(None, "Problem", "Odpowiedź")
    n.grant_call_opened(["a@example.org", "b@example.org"], "Nabór", date(2026, 12, 15), [])
    n.grant_call_opened([], "Nabór", date(2026, 12, 15), [])
    assert [to for to, _ in mailer.sent] == ["test@example.org"] * 2
    assert "Tryb testowy: ta wiadomość trafiłaby do autora zgłoszenia" in mailer.sent[0][1].html


def test_failed_send_is_logged_not_raised(caplog) -> None:
    with caplog.at_level(logging.ERROR):
        make(FakeMailer(fail=True)).idea_replied(AUTHOR, "Pomysł", "x")
    assert "notification not sent" in caplog.text
    # personal data stays out of the log
    assert AUTHOR not in caplog.text


def test_sends_after_response_via_background_tasks() -> None:
    mailer = FakeMailer()
    background = BackgroundTasks()
    Notifier(mailer, background.add_task, WEB).idea_replied(AUTHOR, "Pomysł", "x")
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

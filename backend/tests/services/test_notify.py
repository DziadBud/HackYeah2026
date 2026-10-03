import logging

import pytest
from fastapi import BackgroundTasks

from app.schemas.admin.ideas import IdeaStatus
from app.services import notify
from app.services.notify import Notifier, SmtpMailer, build_mailer

ADMIN = "rops-admin@example.org"


class FakeMailer:
    def __init__(self, fail: bool = False) -> None:
        self.sent: list[tuple[str, str, str]] = []
        self.fail = fail

    def send(self, to: str, subject: str, body: str) -> None:
        if self.fail:
            raise OSError("smtp down")
        self.sent.append((to, subject, body))


def run_now(fn, *args) -> None:
    fn(*args)


def make(mailer: FakeMailer | None) -> Notifier:
    return Notifier(mailer, run_now, ADMIN, "http://web.test/")


@pytest.mark.parametrize(
    "call",
    [
        pytest.param(lambda n: n.new_idea("idea-1", "Opaska dla seniorów"), id="#1 - OK - new idea"),
        pytest.param(lambda n: n.new_problem_report("pr-1", "Brak transportu"), id="#2 - OK - problem report"),
        pytest.param(lambda n: n.new_thread("wibraap", "Pytanie"), id="#3 - OK - new thread"),
        pytest.param(lambda n: n.new_thread_reply("Pytanie"), id="#4 - OK - new reply"),
    ],
)
def test_admin_notifications(call) -> None:
    mailer = FakeMailer()
    call(make(mailer))
    [(to, _, body)] = mailer.sent
    assert to == ADMIN
    assert "http://web.test/admin" in body


def test_author_notifications() -> None:
    mailer = FakeMailer()
    n = make(mailer)
    n.idea_replied("a@example.org", "Pomysł", "Dziękujemy")
    n.idea_status_changed("a@example.org", "Pomysł", IdeaStatus.ACCEPTED)
    n.problem_report_replied("b@example.org", "Problem", "Odpowiedź")
    n.thread_published("c@example.org", "wibraap", "Pytanie")
    assert [m[0] for m in mailer.sent] == ["a@example.org", "a@example.org", "b@example.org", "c@example.org"]
    assert "Dziękujemy" in mailer.sent[0][2]
    assert "przyjęty" in mailer.sent[1][1]
    assert "http://web.test/innowacje/wibraap" in mailer.sent[3][2]


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
    assert [m[0] for m in mailer.sent] == expected


def test_grant_call_opened_one_mail_per_author() -> None:
    mailer = FakeMailer()
    make(mailer).grant_call_opened(["a@example.org", "b@example.org"], "Nabór 2026", "2026-12-15")
    assert [m[0] for m in mailer.sent] == ["a@example.org", "b@example.org"]
    assert all("Nabór 2026" in m[1] for m in mailer.sent)


def test_no_email_no_mail() -> None:
    mailer = FakeMailer()
    make(mailer).idea_replied(None, "Pomysł", "Dziękujemy")
    assert mailer.sent == []


def test_disabled_without_mailer() -> None:
    scheduled = []
    Notifier(None, lambda *a: scheduled.append(a), ADMIN, "http://web.test").new_idea("idea-1", "x")
    assert scheduled == []


def test_no_admin_email_no_mail() -> None:
    mailer = FakeMailer()
    Notifier(mailer, run_now, "", "http://web.test").new_idea("idea-1", "x")
    assert mailer.sent == []


def test_failed_send_is_logged_not_raised(caplog) -> None:
    with caplog.at_level(logging.ERROR):
        make(FakeMailer(fail=True)).idea_replied("a@example.org", "Pomysł", "x")
    assert "notification not sent" in caplog.text
    # personal data stays out of the log
    assert "a@example.org" not in caplog.text


def test_sends_after_response_via_background_tasks() -> None:
    mailer = FakeMailer()
    background = BackgroundTasks()
    Notifier(mailer, background.add_task, ADMIN, "http://web.test").new_idea("idea-1", "x")
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


def test_smtp_mailer_plain(monkeypatch) -> None:
    monkeypatch.setattr(notify.smtplib, "SMTP", FakeSmtp)
    SmtpMailer("mailpit", 1025, "hub@example.org").send("a@example.org", "Temat", "Treść")
    connect, (_, msg) = FakeSmtp.calls
    assert connect == ("connect", "mailpit", 1025)
    assert msg["From"] == "hub@example.org" and msg["To"] == "a@example.org"
    assert msg["Subject"] == "Temat" and msg.get_content().strip() == "Treść"


def test_smtp_mailer_starttls_login(monkeypatch) -> None:
    monkeypatch.setattr(notify.smtplib, "SMTP", FakeSmtp)
    SmtpMailer("smtp.gmail.com", 587, "hub@example.org", "user@example.org", "secret").send(
        "a@example.org", "Temat", "Treść"
    )
    assert [c[0] for c in FakeSmtp.calls] == ["connect", "starttls", "login", "send"]
    assert FakeSmtp.calls[2] == ("login", "user@example.org", "secret")


def test_redirect_sends_everything_to_one_inbox() -> None:
    mailer = FakeMailer()
    n = Notifier(mailer, run_now, ADMIN, "http://web.test", redirect_to="test@example.org")
    n.new_idea("idea-1", "x")
    n.idea_replied("author@example.org", "Pomysł", "Dziękujemy")
    # no author email: still sent, so the reply path is testable
    n.problem_report_replied(None, "Problem", "Odpowiedź")
    n.grant_call_opened(["a@example.org", "b@example.org"], "Nabór", "2026-12-15")
    n.grant_call_opened([], "Nabór", "2026-12-15")
    assert [m[0] for m in mailer.sent] == ["test@example.org"] * 5


def test_build_mailer_off_without_host() -> None:
    assert build_mailer("", 1025, "hub@example.org") is None
    assert isinstance(build_mailer("mailpit", 1025, "hub@example.org"), SmtpMailer)

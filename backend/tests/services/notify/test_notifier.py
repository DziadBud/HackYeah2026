from app.services.notify import notifier
from app.services.notify.notifier import BackgroundNotifier, Mail, RedirectNotifier, SmtpNotifier

MAIL = Mail("t@example.com", "Temat", "Tresc")


class FakeSmtp:
    calls: list[tuple] = []

    def __init__(self, host, port, timeout):
        FakeSmtp.calls.append(("connect", host, port))

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def starttls(self):
        FakeSmtp.calls.append(("starttls",))

    def login(self, user, password):
        FakeSmtp.calls.append(("login", user))

    def send_message(self, msg):
        FakeSmtp.calls.append(("send", msg["From"], msg["To"], msg["Subject"]))


def test_smtp_notifier_uses_starttls_and_login(monkeypatch) -> None:
    FakeSmtp.calls = []
    monkeypatch.setattr(notifier.smtplib, "SMTP", FakeSmtp)

    SmtpNotifier("smtp.gmail.com", 587, "hub@example.com", "app-pass", "hub@example.com").send(MAIL)

    assert FakeSmtp.calls == [
        ("connect", "smtp.gmail.com", 587),
        ("starttls",),
        ("login", "hub@example.com"),
        ("send", "hub@example.com", "t@example.com", "Temat"),
    ]


def test_background_notifier_logs_failures(caplog) -> None:
    class Broken:
        def send(self, mail: Mail) -> None:
            raise OSError("smtp down")

    bg = BackgroundNotifier(Broken())
    bg.send(MAIL)
    bg._pool.shutdown(wait=True)

    assert "mail to t@example.com failed" in caplog.text


def test_redirect_notifier_sends_only_to_test_inbox() -> None:
    sent: list[Mail] = []

    class Recorder:
        def send(self, mail: Mail) -> None:
            sent.append(mail)

    RedirectNotifier(Recorder(), "inbox@example.com").send(MAIL)

    assert sent[0].to == "inbox@example.com"
    assert sent[0].subject == "[test → t@example.com] Temat"
    assert "t@example.com" in sent[0].body and "Tresc" in sent[0].body

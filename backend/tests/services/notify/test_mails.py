import pytest

from app.services.notify import Mail, Mails, Notifications

MAILS = Mails(admin_email="rops@example.com", web_url="http://web/")


@pytest.mark.parametrize(
    "status, subject, link_in_body",
    [
        pytest.param("accepted", "Zapraszamy do testowania innowacji", True, id="#1 - OK - accepted has form link"),
        pytest.param("rejected", "Zgłoszenie do testów", False, id="#2 - OK - rejected"),
        pytest.param("completed", "Dziękujemy za test", False, id="#3 - OK - completed"),
    ],
)
def test_test_signup_status(status, subject, link_in_body) -> None:
    mail = MAILS.test_signup_status("t@example.com", "s-1", "wibraap", "Wibraap", status)
    assert (mail.to, mail.subject) == ("t@example.com", subject)
    assert ("http://web/innovations/wibraap?test_signup=s-1" in mail.body) is link_in_body


def test_admin_mail_links_panel() -> None:
    mail = MAILS.new_idea("Bus dla seniorow")
    assert mail.to == "rops@example.com"
    assert "Bus dla seniorow" in mail.body and "http://web/admin" in mail.body


@pytest.mark.parametrize(
    "mail",
    [
        pytest.param(MAILS.idea_reply(None, "x", "y"), id="#1 - author without email"),
        pytest.param(Mails(admin_email="", web_url="http://web").new_idea("x"), id="#2 - no admin email"),
    ],
)
def test_no_recipient_no_mail(mail) -> None:
    assert mail is None


def test_notifications_skips_none() -> None:
    sent: list[Mail] = []

    class Recorder:
        def send(self, mail: Mail) -> None:
            sent.append(mail)

    notify = Notifications(Recorder(), MAILS)
    notify.send(None)
    notify.send(MAILS.new_idea("x"))
    assert [m.subject for m in sent] == ["Nowy pomysł do przejrzenia"]

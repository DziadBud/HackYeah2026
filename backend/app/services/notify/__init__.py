from functools import cache

from app.config import settings
from app.services.notify.mails import Mails
from app.services.notify.notifier import (
    BackgroundNotifier,
    LogNotifier,
    Mail,
    Notifier,
    RedirectNotifier,
    SmtpNotifier,
)

__all__ = ["Mail", "Mails", "Notifications", "Notifier", "get_notifications"]


@cache
def get_notifier() -> Notifier:
    notifier: Notifier = LogNotifier()
    if settings.smtp_host:
        notifier = SmtpNotifier(
            settings.smtp_host,
            settings.smtp_port,
            settings.smtp_username,
            settings.smtp_password,
            settings.mail_from or settings.smtp_username,
        )
    if settings.mail_redirect_to:
        notifier = RedirectNotifier(notifier, settings.mail_redirect_to)
    return BackgroundNotifier(notifier)


class Notifications:
    """what services hold: builds mails and sends the ones that have a recipient"""

    def __init__(self, notifier: Notifier, mails: Mails) -> None:
        self._notifier = notifier
        self.mails = mails

    def send(self, mail: Mail | None) -> None:
        if mail is not None:
            self._notifier.send(mail)


@cache
def get_notifications() -> Notifications:
    return Notifications(get_notifier(), Mails(settings.admin_notify_email, settings.web_url))

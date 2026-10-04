"""renders every notification with sample data to an html file each; --send mails them to MAIL_REDIRECT_TO"""

import argparse
from datetime import date
from pathlib import Path

from app.config import settings
from app.schemas.admin.common import ChallengeArea
from app.schemas.admin.ideas import IdeaStage, IdeaStatus
from app.schemas.admin.test_signups import TestSignupStatus
from app.services.notify import Notifier, Rendered, build_mailer

ADMIN = "admin"
AUTHOR = "author"
IDEA = "Wspólne obiady dla samotnych seniorów w świetlicy wiejskiej"


def samples(n: Notifier) -> None:
    n.new_idea("8f3c", IDEA, "Raz w tygodniu seniorzy gotują razem z młodzieżą.", "seniorzy 65+", IdeaStage.CONCEPT)
    n.new_problem_report("4a1b", "Seniorzy z naszej gminy nie mają jak dojechać do lekarza.", "Zakliczyn", ChallengeArea.SENIORS)
    n.new_thread("wibraap", "Wibraap", "Czy działa z aparatem słuchowym?", "Pytam dla podopiecznych OPS.")
    n.new_thread_reply("Czy działa z aparatem słuchowym?", "U nas działa, testowaliśmy w DPS.")
    n.new_test_signups("Samotność seniorów na wsi", ["Wibraap", "Paczka dla seniora"])
    n.idea_replied(AUTHOR, IDEA, "Dziękujemy! Zapraszamy na rozmowę w przyszłym tygodniu.")
    n.idea_status_changed(AUTHOR, IDEA, IdeaStatus.ACCEPTED)
    n.idea_status_changed(AUTHOR, IDEA, IdeaStatus.REJECTED)
    n.problem_report_replied(AUTHOR, "Seniorzy nie mają jak dojechać do lekarza.", "Polecamy innowację „Wolontariusz z autem”.")
    n.thread_published(AUTHOR, "wibraap", "Czy działa z aparatem słuchowym?")
    n.reply_published(AUTHOR, "thread-author", "wibraap", "Czy działa z aparatem słuchowym?")
    n.grant_call_opened([AUTHOR], "Nabór ROPS 2026", date(2026, 12, 15), ["Opis problemu", "Budżet"])
    for status in (TestSignupStatus.ACCEPTED, TestSignupStatus.COMPLETED, TestSignupStatus.REJECTED):
        n.test_signup_status(AUTHOR, "5d2e", "wibraap", "Wibraap", status)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=Path("mail-preview"))
    parser.add_argument("--send", action="store_true", help="send every sample to MAIL_REDIRECT_TO")
    args = parser.parse_args()

    rendered: list[Rendered] = []

    class Collect:
        def send(self, to: str, mail: Rendered) -> None:
            rendered.append(mail)

    samples(Notifier(Collect(), lambda fn, *a: fn(*a), ADMIN, settings.web_url))

    args.out.mkdir(parents=True, exist_ok=True)
    for i, mail in enumerate(rendered, 1):
        (args.out / f"{i:02d}.html").write_text(mail.html)
    print(f"{len(rendered)} mails written to {args.out}/")

    if args.send:
        mailer = build_mailer(
            settings.smtp_host, settings.smtp_port, settings.mail_from, settings.smtp_username, settings.smtp_password
        )
        if mailer is None or not settings.mail_redirect_to:
            raise SystemExit("--send needs SMTP_HOST, MAIL_FROM and MAIL_REDIRECT_TO")
        for mail in rendered:
            mailer.send(settings.mail_redirect_to, mail)
        print(f"sent {len(rendered)} mails to MAIL_REDIRECT_TO")


if __name__ == "__main__":
    main()

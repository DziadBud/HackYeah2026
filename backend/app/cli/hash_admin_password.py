import argparse
import getpass
import json
import sys

from app.services.admin.auth import hash_password


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="python -m app.cli.hash_admin_password",
        description="print an ADMIN_ACCOUNTS entry for .env",
    )
    parser.add_argument("email")
    email = parser.parse_args().email.strip().lower()

    password = getpass.getpass("password: ")
    if len(password) < 12:
        sys.exit("password must be at least 12 characters")
    if password != getpass.getpass("repeat: "):
        sys.exit("passwords do not match")
    # single quotes keep docker compose and dotenv from expanding the $ in the hash
    print(f"ADMIN_ACCOUNTS='{json.dumps({email: hash_password(password)})}'")


if __name__ == "__main__":
    main()

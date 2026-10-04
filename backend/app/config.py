from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "hackyeah-api"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://hackyeah:hackyeah@localhost:5432/hackyeah"

    # one shared admin login from env; empty means nobody can log in
    admin_username: str = ""
    admin_password: str = ""
    admin_session_ttl_hours: int = 8
    admin_session_idle_minutes: int = 30
    admin_login_max_failures: int = 5
    admin_login_window_minutes: int = 15
    # demo only: skip the admin login. honoured only together with debug=true
    admin_auth_disabled: bool = False

    rag_url: str = "http://localhost:8001"
    # embedding a 10 mb pdf on cpu can take minutes
    rag_timeout_seconds: float = 300
    # /query embeds the text and asks rag's llm (ollama on cpu) for the answer
    rag_query_timeout_seconds: float = 60
    # uploaded pdfs are kept on disk so an innovation can be re-embedded later
    upload_dir: str = "/data/uploads"
    max_upload_bytes: int = 10 * 1024 * 1024
    # photos and pdfs shipped with the seeded innovations (backend/seed_media/<id>/);
    # an admin-uploaded pdf in upload_dir takes precedence
    seed_media_dir: str = str(Path(__file__).resolve().parents[1] / "seed_media")

    # grant-application drafts (Gemini)
    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.5-flash"

    # notifications (R10/R12); empty smtp_host or mail_from turns them off.
    # no default addresses on purpose: a fallback could mail a real inbox by accident
    smtp_host: str = ""
    smtp_port: int = 1025
    # set for a real relay (gmail: 587, app password); empty for mailpit
    smtp_username: str = ""
    smtp_password: str = ""
    mail_from: str = ""
    # testing: send every notification here instead of the real recipient
    mail_redirect_to: str = ""
    # public frontend, for links in mails
    web_url: str = "http://localhost:3000"
    # this api as seen from a browser, for the rating links in tester mails
    api_url: str = "http://localhost:8000"


settings = Settings()

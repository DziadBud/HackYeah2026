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
    # uploaded pdfs are kept on disk so an innovation can be re-embedded later
    upload_dir: str = "/data/uploads"
    max_upload_bytes: int = 10 * 1024 * 1024

    gemini_api_key: str = ""
    gemini_model: str = "gemini-3.8-flash"


settings = Settings()

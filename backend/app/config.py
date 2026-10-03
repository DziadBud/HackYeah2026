from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "hackyeah-api"
    debug: bool = False
    cors_origins: list[str] = ["http://localhost:3000"]
    database_url: str = "postgresql+psycopg://hackyeah:hackyeah@localhost:5432/hackyeah"

    # email -> argon2id hash, generate with `make hash-password`
    admin_accounts: dict[str, str] = {}
    admin_session_ttl_hours: int = 8
    admin_session_idle_minutes: int = 30
    admin_login_max_failures: int = 5
    admin_login_window_minutes: int = 15

    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"


settings = Settings()

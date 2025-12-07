from pydantic.v1 import BaseSettings
from os import path


class Settings(BaseSettings):
    # Telegram auth
    TELEGRAM_API_TOKEN: str
    TELEGRAM_API_SERVER: str
    TELEGRAM_API_PORT: int
    BOT_ADMINS: list

    @property
    def api_server_url(self):
        return f"http://{self.TELEGRAM_API_SERVER}:{self.TELEGRAM_API_PORT}"

    # Path to webhook route, on which Telegram will send requests
    WEBHOOK_PATH: str | None
    # Secret key to validate requests from Telegram (optional)
    WEBHOOK_SECRET: str | None
    WEBHOOK_PORT: int | None
    # Base URL for webhook will be used to generate webhook URL for Telegram,
    # in this example it is used public DNS with HTTPS support
    BASE_WEBHOOK_URL: str | None

    @property
    def webhook(self):
        return f"{self.BASE_WEBHOOK_URL}:{self.WEBHOOK_PORT}{self.WEBHOOK_PATH}"

    class Config:
        env_file = ".env" if path.exists(".env") else None


settings = Settings()

from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseModel):
	database_url: str = os.getenv("DATABASE_URL", "sqlite:///./jobs.db")
	cors_allow_origins: list[str] = (
		os.getenv("CORS_ALLOW_ORIGINS", "http://localhost:3000, http://127.0.0.1:3000")
		.replace(" ", "")
		.split(",")
	)

	# Selenium
	selenium_headless: bool = os.getenv("SELENIUM_HEADLESS", "true").lower() == "true"
	chrome_driver_path: str | None = os.getenv("CHROME_DRIVER_PATH")

	# Alerting
	email_enabled: bool = os.getenv("EMAIL_ENABLED", "false").lower() == "true"
	smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
	smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
	smtp_use_tls: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
	sender_email: str | None = os.getenv("SENDER_EMAIL")
	sender_password: str | None = os.getenv("SENDER_PASSWORD")
	receiver_email: str | None = os.getenv("RECEIVER_EMAIL")

	telegram_enabled: bool = os.getenv("TELEGRAM_ENABLED", "false").lower() == "true"
	telegram_bot_token: str | None = os.getenv("TELEGRAM_BOT_TOKEN")
	telegram_chat_id: str | None = os.getenv("TELEGRAM_CHAT_ID")

	# Scheduler
	schedule_cron: str = os.getenv("SCHEDULE_CRON", "0 8 * * *")


settings = Settings()

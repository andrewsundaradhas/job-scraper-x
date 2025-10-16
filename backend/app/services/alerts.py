from __future__ import annotations

import smtplib
from email.mime.text import MIMEText
from typing import Optional
import requests

from sqlalchemy.orm import Session

from ..config import settings
from .. import crud


def send_email_alert(db: Session, job_id: int, subject: str, body: str) -> bool:
	if not settings.email_enabled:
		return False
	if not (settings.sender_email and settings.sender_password and settings.receiver_email):
		return False

	msg = MIMEText(body, "html")
	msg["Subject"] = subject
	msg["From"] = settings.sender_email
	msg["To"] = settings.receiver_email

	try:
		smtp = smtplib.SMTP(settings.smtp_server, settings.smtp_port)
		if settings.smtp_use_tls:
			smtp.starttls()
		smtp.login(settings.sender_email, settings.sender_password)
		smtp.sendmail(settings.sender_email, [settings.receiver_email], msg.as_string())
		smtp.quit()
		crud.create_alert_log(db, job_id=job_id, channel="email", status="sent", message=subject)
		return True
	except Exception as e:
		crud.create_alert_log(db, job_id=job_id, channel="email", status="failed", message=str(e))
		return False


def send_telegram_alert(db: Session, job_id: int, text: str) -> bool:
	if not settings.telegram_enabled:
		return False
	if not (settings.telegram_bot_token and settings.telegram_chat_id):
		return False
	try:
		resp = requests.post(
			f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage",
			json={"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML"},
			timeout=10,
		)
		ok = resp.ok
		crud.create_alert_log(db, job_id=job_id, channel="telegram", status="sent" if ok else "failed", message=text[:180])
		return ok
	except Exception as e:
		crud.create_alert_log(db, job_id=job_id, channel="telegram", status="failed", message=str(e))
		return False

from __future__ import annotations

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session

from .config import settings
from .database import SessionLocal
from .services.scraper import scrape_linkedin_jobs
from . import crud
from .schemas import JobCreate
from datetime import date


scheduler: BackgroundScheduler | None = None


def run_daily_scrape(keywords: str, location: str):
	db: Session = SessionLocal()
	try:
		results = scrape_linkedin_jobs(keywords=keywords, location=location, max_pages=3)
		for r in results:
			posted_date = None
			if r.get("posted_date"):
				try:
					posted_date = date.fromisoformat(r["posted_date"])  # yyyy-mm-dd
				except Exception:
					posted_date = None
			job = JobCreate(
				title=r.get("title") or "",
				company=r.get("company"),
				location=r.get("location"),
				posted_date=posted_date,
				job_link=r.get("job_link") or "",
				experience_level=r.get("experience_level"),
				job_type=r.get("job_type"),
				keywords=r.get("keywords"),
			)
			crud.create_job_if_not_exists(db, job)
	finally:
		db.close()


def start_scheduler():
	global scheduler
	if scheduler is not None:
		return scheduler
	scheduler = BackgroundScheduler()
	# Defaults: user can later configure via admin
	cron = settings.schedule_cron
	# Example default keywords/location; can be overridden later via persisted config
	keywords = "Software Engineer"
	location = "Remote"
	scheduler.add_job(run_daily_scrape, CronTrigger.from_crontab(cron), kwargs={"keywords": keywords, "location": location}, id="daily_scrape", replace_existing=True)
	scheduler.start()
	return scheduler

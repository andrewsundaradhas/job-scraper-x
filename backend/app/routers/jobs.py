from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime, date

from ..database import get_db
from .. import crud
from ..schemas import JobRead, JobFilter, JobCreate
from ..services.scraper import scrape_linkedin_jobs
from ..services.alerts import send_email_alert, send_telegram_alert

router = APIRouter(tags=["jobs"])


@router.get("/jobs", response_model=List[JobRead])
def get_jobs(
	keyword: str | None = None,
	company: str | None = None,
	location: str | None = None,
	date_from: str | None = None,
	date_to: str | None = None,
	limit: int = 50,
	offset: int = 0,
	order_by: str | None = "-created_at",
	db: Session = Depends(get_db),
):
	filters = JobFilter(
		keyword=keyword,
		company=company,
		location=location,
		limit=min(max(limit, 1), 200),
		offset=max(offset, 0),
		order_by=order_by,
	)
	return crud.list_jobs(db, filters)


@router.post("/scrape")
def trigger_scrape(keywords: str, location: str, db: Session = Depends(get_db)):
	results = scrape_linkedin_jobs(keywords=keywords, location=location, max_pages=3)
	new_jobs = []
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
		created = crud.create_job_if_not_exists(db, job)
		if created:
			new_jobs.append(created)

	# Alerts for new jobs
	for job in new_jobs:
		subject = f"New Job: {job.title} at {job.company or ''}".strip()
		body = f"<b>{job.title}</b> at {job.company or ''}<br/>{job.location or ''}<br/><a href='{job.job_link}'>Open</a>"
		send_email_alert(db, job.id, subject, body)
		text = f"New Job: {job.title} at {job.company or ''}\n{job.location or ''}\n{job.job_link}"
		send_telegram_alert(db, job.id, text)

	return {"found": len(results), "created": len(new_jobs)}

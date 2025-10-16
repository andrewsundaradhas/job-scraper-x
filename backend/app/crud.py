from typing import Iterable, List, Optional, Sequence, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import select, asc, desc, func
from datetime import date

from . import models
from .schemas import JobCreate, JobFilter


def _order_clause(model, order_by: Optional[str]):
	if not order_by:
		return desc(model.created_at)
	field = order_by.lstrip("+-")
	direction = desc if order_by.startswith("-") else asc
	column = getattr(model, field, None)
	return direction(column) if column is not None else desc(model.created_at)


def create_job_if_not_exists(db: Session, job: JobCreate) -> models.Job | None:
	# unique by job_link
	existing = db.execute(
		select(models.Job).where(models.Job.job_link == job.job_link)
	).scalar_one_or_none()
	if existing:
		return None
	new_job = models.Job(
		title=job.title,
		company=job.company,
		location=job.location,
		posted_date=job.posted_date,
		job_link=job.job_link,
		experience_level=job.experience_level,
		job_type=job.job_type,
		keywords=job.keywords,
	)
	db.add(new_job)
	db.commit()
	db.refresh(new_job)
	return new_job


def list_jobs(db: Session, filters: JobFilter):
	stmt = select(models.Job)
	if filters.keyword:
		like = f"%{filters.keyword}%"
		stmt = stmt.where(
			(models.Job.title.ilike(like)) | (models.Job.keywords.ilike(like))
		)
	if filters.company:
		stmt = stmt.where(models.Job.company == filters.company)
	if filters.location:
		stmt = stmt.where(models.Job.location == filters.location)
	if filters.date_from:
		stmt = stmt.where(models.Job.posted_date >= filters.date_from)
	if filters.date_to:
		stmt = stmt.where(models.Job.posted_date <= filters.date_to)
	stmt = stmt.order_by(_order_clause(models.Job, filters.order_by)).offset(filters.offset).limit(filters.limit)
	rows = db.execute(stmt).scalars().all()
	return rows


def count_jobs(db: Session, filters: JobFilter) -> int:
	stmt = select(func.count(models.Job.id))
	if filters.keyword:
		like = f"%{filters.keyword}%"
		stmt = stmt.where(
			(models.Job.title.ilike(like)) | (models.Job.keywords.ilike(like))
		)
	if filters.company:
		stmt = stmt.where(models.Job.company == filters.company)
	if filters.location:
		stmt = stmt.where(models.Job.location == filters.location)
	if filters.date_from:
		stmt = stmt.where(models.Job.posted_date >= filters.date_from)
	if filters.date_to:
		stmt = stmt.where(models.Job.posted_date <= filters.date_to)
	return db.execute(stmt).scalar_one() or 0


def create_alert_log(db: Session, job_id: int, channel: str, status: str, message: str | None = None) -> models.AlertLog:
	log = models.AlertLog(job_id=job_id, channel=channel, status=status, message=message)
	db.add(log)
	db.commit()
	db.refresh(log)
	return log


def list_alert_logs(db: Session, limit: int = 100, offset: int = 0):
	stmt = select(models.AlertLog).order_by(desc(models.AlertLog.created_at)).offset(offset).limit(limit)
	return db.execute(stmt).scalars().all()

from sqlalchemy import Column, Integer, String, DateTime, Text, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base


class Job(Base):
	__tablename__ = "jobs"
	__table_args__ = (
		UniqueConstraint("job_link", name="uq_jobs_job_link"),
	)

	id = Column(Integer, primary_key=True, index=True)
	title = Column(String(255), nullable=False)
	company = Column(String(255), nullable=True)
	location = Column(String(255), nullable=True)
	posted_date = Column(Date, nullable=True)
	job_link = Column(Text, nullable=False)
	experience_level = Column(String(100), nullable=True)
	job_type = Column(String(100), nullable=True)
	keywords = Column(String(255), nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	alerts = relationship("AlertLog", back_populates="job", cascade="all, delete-orphan")


class AlertLog(Base):
	__tablename__ = "alert_logs"

	id = Column(Integer, primary_key=True, index=True)
	job_id = Column(Integer, ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False, index=True)
	channel = Column(String(50), nullable=False)
	status = Column(String(50), nullable=False, default="sent")
	message = Column(Text, nullable=True)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	job = relationship("Job", back_populates="alerts")

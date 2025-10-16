from pydantic import BaseModel, HttpUrl, field_validator
from datetime import date, datetime
from typing import Optional, List


class JobBase(BaseModel):
	title: str
	company: Optional[str] = None
	location: Optional[str] = None
	posted_date: Optional[date] = None
	job_link: str
	experience_level: Optional[str] = None
	job_type: Optional[str] = None
	keywords: Optional[str] = None

	@field_validator("job_link")
	@classmethod
	def validate_job_link(cls, v: str) -> str:
		# basic sanity; LinkedIn links may be long and with params
		if not v.startswith("http"):
			raise ValueError("job_link must be a URL")
		return v


class JobCreate(JobBase):
	pass


class JobRead(JobBase):
	id: int
	created_at: datetime

	class Config:
		from_attributes = True


class JobFilter(BaseModel):
	keyword: Optional[str] = None
	company: Optional[str] = None
	date_from: Optional[date] = None
	date_to: Optional[date] = None
	location: Optional[str] = None
	limit: int = 50
	offset: int = 0
	order_by: Optional[str] = "-created_at"


class AlertLogRead(BaseModel):
	id: int
	job_id: int
	channel: str
	status: str
	message: Optional[str] = None
	created_at: datetime

	class Config:
		from_attributes = True

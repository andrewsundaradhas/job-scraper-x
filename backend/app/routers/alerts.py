from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from .. import crud
from ..schemas import AlertLogRead

router = APIRouter(tags=["alerts"])


@router.get("/alerts", response_model=List[AlertLogRead])
def get_alerts(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)):
	return crud.list_alert_logs(db, limit=limit, offset=offset)

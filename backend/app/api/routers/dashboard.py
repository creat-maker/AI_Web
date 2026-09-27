from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_staff
from app.db.session import get_db
from app.services.dashboard_service import get_dashboard_activity, get_dashboard_summary


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def summary(
    current_user: dict = Depends(require_staff),
    db: Session = Depends(get_db),
):
    return get_dashboard_summary(db)


@router.get("/activity")
def activity(
    current_user: dict = Depends(require_staff),
    db: Session = Depends(get_db),
):
    return get_dashboard_activity(db)

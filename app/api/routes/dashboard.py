from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_permission
from app.core.database import get_db
from app.models.user import User
from app.schemas.dashboard import SummaryResponse
from app.services.dashboard_service import get_dashboard_summary

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=SummaryResponse)
def summary(
    db: Session = Depends(get_db),
    _: User = Depends(require_permission("dashboard:read")),
) -> SummaryResponse:
    return get_dashboard_summary(db)

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.dashboard import DashboardIAMetricasResponse
from app.services.dashboard_service import build_dashboard_metrics

router = APIRouter(prefix='/v1/dashboard', tags=['dashboard'])


@router.get('/ia', response_model=DashboardIAMetricasResponse)
def get_ai_dashboard(
    janela_dias: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    return build_dashboard_metrics(db, janela_dias)

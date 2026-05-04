from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.recommendation import Incident
from app.schemas.incidents import IncidentResponse, IncidentSummaryResponse

router = APIRouter(prefix='/v1/incidentes', tags=['incidentes'])


@router.get('', response_model=list[IncidentSummaryResponse])
def list_incidents(
    limit: int = Query(default=20, ge=1, le=100),
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Incident)

    if status:
        stmt = stmt.where(Incident.status == status)

    if search:
        term = f'%{search.strip()}%'
        stmt = stmt.where(
            or_(
                Incident.title.ilike(term),
                Incident.module_name.ilike(term),
                Incident.functionality_name.ilike(term),
            )
        )

    stmt = stmt.order_by(Incident.created_at.desc()).limit(limit)
    incidents = list(db.scalars(stmt).all())
    return [
        IncidentSummaryResponse(
            id=item.id,
            titulo=item.title,
            modulo=item.module_name,
            funcionalidade=item.functionality_name,
            severidade=item.severity,
            status=item.status,
            score_atual=item.current_score,
        )
        for item in incidents
    ]


@router.get('/{incident_id}', response_model=IncidentResponse)
def get_incident(incident_id: int, db: Session = Depends(get_db)):
    incident = db.get(Incident, incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail='Incidente não encontrado.')
    return IncidentResponse(
        id=incident.id,
        titulo=incident.title,
        modulo=incident.module_name,
        funcionalidade=incident.functionality_name,
        severidade=incident.severity,
        status=incident.status,
        score_atual=incident.current_score,
        resumo_contexto=incident.context_summary,
        sistema_origem=incident.source_system,
        criado_em=incident.created_at,
    )

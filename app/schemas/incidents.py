from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

IncidentSeverity = Literal["baixa", "media", "alta", "critica"]
IncidentStatus = Literal["aberto", "em_analise", "resolvido", "monitorando"]


class IncidentResponse(BaseModel):
    id: int
    titulo: str
    modulo: str
    funcionalidade: str
    severidade: IncidentSeverity
    status: IncidentStatus
    score_atual: float | None
    resumo_contexto: str | None
    sistema_origem: str | None
    criado_em: datetime


class IncidentSummaryResponse(BaseModel):
    id: int
    titulo: str
    modulo: str
    funcionalidade: str
    severidade: IncidentSeverity
    status: IncidentStatus
    score_atual: float | None

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

RecommendationType = Literal["hotfix", "proxima_versao", "backlog", "monitorar"]


class RecommendationCreate(BaseModel):
    id_incidente: int = Field(..., ge=1)
    titulo: str = Field(..., min_length=3, max_length=255)
    contexto_incidente: str | None = None
    tipo_recomendacao: RecommendationType
    confianca_ia: float = Field(..., ge=0, le=1)
    recomendacao: str = Field(..., min_length=3)
    modelo: str | None = Field(default=None, max_length=100)
    score_inicial: float | None = Field(default=None, ge=0, le=1)


class RecommendationResponse(BaseModel):
    id: int
    id_incidente: int
    titulo: str
    contexto_incidente: str | None
    tipo_recomendacao: RecommendationType
    confianca_ia: float
    recomendacao: str
    modelo: str | None
    score_inicial: float | None
    criado_em: datetime


class RecommendationDecisionUpsert(BaseModel):
    aceita: bool
    motivo_decisao: str | None = None
    decidido_por: str | None = Field(default=None, max_length=120)


class RecommendationDecisionResponse(BaseModel):
    id: int
    id_recomendacao: int
    aceita: bool
    motivo_decisao: str | None
    decidido_por: str | None
    decidido_em: datetime


class RecommendationOutcomeUpsert(BaseModel):
    foi_aplicada: bool
    versao_aplicada: str | None = Field(default=None, max_length=50)
    outcome_positivo: bool | None = None
    score_pos_correcao: float | None = Field(default=None, ge=0, le=1)
    observacao: str | None = None


class RecommendationOutcomeResponse(BaseModel):
    id: int
    id_recomendacao: int
    foi_aplicada: bool
    versao_aplicada: str | None
    outcome_positivo: bool | None
    score_pos_correcao: float | None
    avaliado_em: datetime
    observacao: str | None


class RecommendationDecisionEmbedded(BaseModel):
    id: int
    aceita: bool
    motivo_decisao: str | None
    decidido_por: str | None
    decidido_em: datetime


class RecommendationOutcomeEmbedded(BaseModel):
    id: int
    foi_aplicada: bool
    versao_aplicada: str | None
    outcome_positivo: bool | None
    score_pos_correcao: float | None
    avaliado_em: datetime
    observacao: str | None


class RecommendationDetailResponse(BaseModel):
    id: int
    id_incidente: int
    titulo: str
    contexto_incidente: str | None
    tipo_recomendacao: RecommendationType
    confianca_ia: float
    recomendacao: str
    modelo: str | None
    score_inicial: float | None
    criado_em: datetime
    decisao: RecommendationDecisionEmbedded | None = None
    outcome: RecommendationOutcomeEmbedded | None = None

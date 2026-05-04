from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Incident(Base):
    __tablename__ = 'incident'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column('titulo', String(255), nullable=False, index=True)
    module_name: Mapped[str] = mapped_column('modulo', String(120), nullable=False, index=True)
    functionality_name: Mapped[str] = mapped_column('funcionalidade', String(120), nullable=False, index=True)
    severity: Mapped[str] = mapped_column('severidade', String(30), nullable=False, index=True)
    status: Mapped[str] = mapped_column('status', String(30), nullable=False, default='aberto', index=True)
    current_score: Mapped[float | None] = mapped_column('score_atual', Float, nullable=True)
    context_summary: Mapped[str | None] = mapped_column('resumo_contexto', Text, nullable=True)
    source_system: Mapped[str | None] = mapped_column('sistema_origem', String(120), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    recommendations: Mapped[list['Recommendation']] = relationship(back_populates='incident')


class Recommendation(Base):
    __tablename__ = 'recommendation_ia'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    incident_id: Mapped[int] = mapped_column('id_incidente', ForeignKey('incident.id'), nullable=False, index=True)
    title: Mapped[str] = mapped_column('titulo', String(255), nullable=False)
    incident_context: Mapped[str | None] = mapped_column('contexto_incidente', Text, nullable=True)
    recommendation_type: Mapped[str] = mapped_column('tipo_recomendacao', String(50), nullable=False, index=True)
    confidence_ai: Mapped[float] = mapped_column('confianca_ia', Float, nullable=False, index=True)
    recommendation_text: Mapped[str] = mapped_column('recomendacao', Text, nullable=False)
    model_name: Mapped[str | None] = mapped_column('modelo', String(100), nullable=True)
    score_initial: Mapped[float | None] = mapped_column('score_inicial', Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    incident: Mapped[Incident] = relationship(back_populates='recommendations')
    decision: Mapped['RecommendationDecision | None'] = relationship(
        back_populates='recommendation', uselist=False, cascade='all, delete-orphan'
    )
    outcome: Mapped['RecommendationOutcome | None'] = relationship(
        back_populates='recommendation', uselist=False, cascade='all, delete-orphan'
    )


class RecommendationDecision(Base):
    __tablename__ = 'recommendation_decision'
    __table_args__ = (UniqueConstraint('id_recomendacao', name='uq_decision_recommendation'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recommendation_id: Mapped[int] = mapped_column('id_recomendacao', ForeignKey('recommendation_ia.id'), nullable=False)
    accepted: Mapped[bool] = mapped_column('aceita', Boolean, nullable=False)
    decision_reason: Mapped[str | None] = mapped_column('motivo_decisao', Text, nullable=True)
    decided_by: Mapped[str | None] = mapped_column('decidido_por', String(120), nullable=True)
    decided_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)

    recommendation: Mapped[Recommendation] = relationship(back_populates='decision')


class RecommendationOutcome(Base):
    __tablename__ = 'recommendation_outcome'
    __table_args__ = (UniqueConstraint('id_recomendacao', name='uq_outcome_recommendation'),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    recommendation_id: Mapped[int] = mapped_column('id_recomendacao', ForeignKey('recommendation_ia.id'), nullable=False)
    applied: Mapped[bool] = mapped_column('foi_aplicada', Boolean, nullable=False)
    release_version: Mapped[str | None] = mapped_column('versao_aplicada', String(50), nullable=True)
    outcome_positive: Mapped[bool | None] = mapped_column('outcome_positivo', Boolean, nullable=True, index=True)
    score_after: Mapped[float | None] = mapped_column('score_pos_correcao', Float, nullable=True)
    evaluated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, nullable=False, index=True)
    observation: Mapped[str | None] = mapped_column('observacao', Text, nullable=True)

    recommendation: Mapped[Recommendation] = relationship(back_populates='outcome')

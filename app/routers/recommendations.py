from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.database import get_db
from app.models.recommendation import Incident, Recommendation, RecommendationDecision, RecommendationOutcome
from app.schemas.recommendation import (
    RecommendationCreate,
    RecommendationDecisionEmbedded,
    RecommendationDecisionResponse,
    RecommendationDecisionUpsert,
    RecommendationDetailResponse,
    RecommendationOutcomeEmbedded,
    RecommendationOutcomeResponse,
    RecommendationOutcomeUpsert,
    RecommendationResponse,
)

router = APIRouter(prefix='/v1/recomendacoes', tags=['recomendacoes'])


def _serialize_detail(recommendation: Recommendation) -> RecommendationDetailResponse:
    decision = recommendation.decision
    outcome = recommendation.outcome

    return RecommendationDetailResponse(
        id=recommendation.id,
        id_incidente=recommendation.incident_id,
        titulo=recommendation.title,
        contexto_incidente=recommendation.incident_context,
        tipo_recomendacao=recommendation.recommendation_type,
        confianca_ia=recommendation.confidence_ai,
        recomendacao=recommendation.recommendation_text,
        modelo=recommendation.model_name,
        score_inicial=recommendation.score_initial,
        criado_em=recommendation.created_at,
        decisao=(
            RecommendationDecisionEmbedded(
                id=decision.id,
                aceita=decision.accepted,
                motivo_decisao=decision.decision_reason,
                decidido_por=decision.decided_by,
                decidido_em=decision.decided_at,
            )
            if decision
            else None
        ),
        outcome=(
            RecommendationOutcomeEmbedded(
                id=outcome.id,
                foi_aplicada=outcome.applied,
                versao_aplicada=outcome.release_version,
                outcome_positivo=outcome.outcome_positive,
                score_pos_correcao=outcome.score_after,
                avaliado_em=outcome.evaluated_at,
                observacao=outcome.observation,
            )
            if outcome
            else None
        ),
    )


@router.get('', response_model=list[RecommendationDetailResponse])
def list_recommendations(
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    stmt = (
        select(Recommendation)
        .options(selectinload(Recommendation.decision), selectinload(Recommendation.outcome), selectinload(Recommendation.incident))
        .order_by(Recommendation.created_at.desc())
        .limit(limit)
    )
    recommendations = list(db.scalars(stmt).all())
    return [_serialize_detail(item) for item in recommendations]


@router.get('/{recommendation_id}', response_model=RecommendationDetailResponse)
def get_recommendation(recommendation_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Recommendation)
        .where(Recommendation.id == recommendation_id)
        .options(selectinload(Recommendation.decision), selectinload(Recommendation.outcome), selectinload(Recommendation.incident))
    )
    recommendation = db.scalars(stmt).first()
    if not recommendation:
        raise HTTPException(status_code=404, detail='Recomendação não encontrada.')
    return _serialize_detail(recommendation)


@router.post('', response_model=RecommendationResponse, status_code=status.HTTP_201_CREATED)
def create_recommendation(payload: RecommendationCreate, db: Session = Depends(get_db)):
    incident = db.get(Incident, payload.id_incidente)
    if not incident:
        raise HTTPException(status_code=404, detail='Incidente não encontrado para vincular à recomendação.')

    recommendation = Recommendation(
        incident_id=payload.id_incidente,
        title=payload.titulo,
        incident_context=payload.contexto_incidente,
        recommendation_type=payload.tipo_recomendacao,
        confidence_ai=payload.confianca_ia,
        recommendation_text=payload.recomendacao,
        model_name=payload.modelo,
        score_initial=payload.score_inicial,
    )
    db.add(recommendation)
    db.commit()
    db.refresh(recommendation)
    return RecommendationResponse(
        id=recommendation.id,
        id_incidente=recommendation.incident_id,
        titulo=recommendation.title,
        contexto_incidente=recommendation.incident_context,
        tipo_recomendacao=recommendation.recommendation_type,
        confianca_ia=recommendation.confidence_ai,
        recomendacao=recommendation.recommendation_text,
        modelo=recommendation.model_name,
        score_inicial=recommendation.score_initial,
        criado_em=recommendation.created_at,
    )


@router.post('/{recommendation_id}/decisao', response_model=RecommendationDecisionResponse)
def upsert_decision(recommendation_id: int, payload: RecommendationDecisionUpsert, db: Session = Depends(get_db)):
    recommendation = db.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail='Recomendação não encontrada.')

    decision = recommendation.decision
    if not decision:
        decision = RecommendationDecision(recommendation_id=recommendation_id)
        db.add(decision)

    decision.accepted = payload.aceita
    decision.decision_reason = payload.motivo_decisao
    decision.decided_by = payload.decidido_por
    db.commit()
    db.refresh(decision)
    return RecommendationDecisionResponse(
        id=decision.id,
        id_recomendacao=decision.recommendation_id,
        aceita=decision.accepted,
        motivo_decisao=decision.decision_reason,
        decidido_por=decision.decided_by,
        decidido_em=decision.decided_at,
    )


@router.post('/{recommendation_id}/outcome', response_model=RecommendationOutcomeResponse)
def upsert_outcome(recommendation_id: int, payload: RecommendationOutcomeUpsert, db: Session = Depends(get_db)):
    recommendation = db.get(Recommendation, recommendation_id)
    if not recommendation:
        raise HTTPException(status_code=404, detail='Recomendação não encontrada.')

    outcome = recommendation.outcome
    if not outcome:
        outcome = RecommendationOutcome(recommendation_id=recommendation_id)
        db.add(outcome)

    outcome.applied = payload.foi_aplicada
    outcome.release_version = payload.versao_aplicada
    outcome.outcome_positive = payload.outcome_positivo
    outcome.score_after = payload.score_pos_correcao
    outcome.observation = payload.observacao
    db.commit()
    db.refresh(outcome)
    return RecommendationOutcomeResponse(
        id=outcome.id,
        id_recomendacao=outcome.recommendation_id,
        foi_aplicada=outcome.applied,
        versao_aplicada=outcome.release_version,
        outcome_positivo=outcome.outcome_positive,
        score_pos_correcao=outcome.score_after,
        avaliado_em=outcome.evaluated_at,
        observacao=outcome.observation,
    )

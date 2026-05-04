from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from math import floor
from statistics import mean
from typing import Iterable

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.recommendation import Recommendation


def _round(value: float | None, digits: int = 3) -> float | None:
    if value is None:
        return None
    return round(float(value), digits)


def _safe_ratio(numerator: int, denominator: int) -> float:
    if denominator == 0:
        return 0.0
    return numerator / denominator


def _bucket_label(dt: datetime) -> str:
    return dt.strftime('%m-%d')


def _iter_filtered_recommendations(db: Session, window_days: int) -> list[Recommendation]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=window_days)
    stmt = (
        select(Recommendation)
        .where(Recommendation.created_at >= cutoff)
        .options(selectinload(Recommendation.decision), selectinload(Recommendation.outcome))
        .order_by(Recommendation.created_at.asc())
    )
    return list(db.scalars(stmt).all())


def _build_calibration_bins(recommendations: Iterable[Recommendation]) -> tuple[list[dict], float, float]:
    scored = [
        rec
        for rec in recommendations
        if rec.outcome and rec.outcome.applied and rec.outcome.outcome_positive is not None
    ]
    if not scored:
        return [], 0.0, 0.0

    buckets: dict[int, list[Recommendation]] = defaultdict(list)
    for rec in scored:
        bucket = min(floor(rec.confidence_ai * 5), 4)
        buckets[bucket].append(rec)

    bins: list[dict] = []
    total_items = len(scored)
    ece = 0.0
    brier_terms: list[float] = []

    for idx in sorted(buckets):
        items = buckets[idx]
        confidences = [item.confidence_ai for item in items]
        outcomes = [1.0 if item.outcome and item.outcome.outcome_positive else 0.0 for item in items]
        avg_conf = mean(confidences)
        avg_outcome = mean(outcomes)
        bins.append(
            {
                'confianca_media': _round(avg_conf),
                'taxa_outcome_positivo': _round(avg_outcome),
                'n_amostras': len(items),
            }
        )
        ece += (len(items) / total_items) * abs(avg_conf - avg_outcome)
        brier_terms.extend((conf - out) ** 2 for conf, out in zip(confidences, outcomes, strict=True))

    brier = mean(brier_terms) if brier_terms else 0.0
    return bins, _round(ece), _round(brier)


def _build_type_metrics(recommendations: Iterable[Recommendation]) -> list[dict]:
    grouped: dict[str, list[Recommendation]] = defaultdict(list)
    for rec in recommendations:
        grouped[rec.recommendation_type].append(rec)

    label_map = {
        'hotfix': 'Hotfix',
        'proxima_versao': 'Próx. versão',
        'backlog': 'Backlog',
        'monitorar': 'Monitorar',
    }

    result = []
    for rec_type, items in grouped.items():
        decisions = [item for item in items if item.decision is not None]
        accepted = [item for item in decisions if item.decision and item.decision.accepted]
        evaluated = [
            item
            for item in accepted
            if item.outcome and item.outcome.applied and item.outcome.outcome_positive is not None
        ]
        positives = [item for item in evaluated if item.outcome and item.outcome.outcome_positive]
        result.append(
            {
                'tipo': label_map.get(rec_type, rec_type),
                'taxa_aceitacao': _round(_safe_ratio(len(accepted), len(decisions))),
                'taxa_eficacia': _round(_safe_ratio(len(positives), len(evaluated))) if evaluated else None,
                'amostras': len(items),
            }
        )
    order = {'Hotfix': 0, 'Próx. versão': 1, 'Backlog': 2, 'Monitorar': 3}
    return sorted(result, key=lambda item: order.get(item['tipo'], 99))


def _build_trend(recommendations: Iterable[Recommendation]) -> list[dict]:
    buckets: dict[str, dict[str, list[Recommendation]]] = defaultdict(lambda: {'decision': [], 'evaluated': []})

    for rec in recommendations:
        bucket_date = rec.decision.decided_at if rec.decision else rec.created_at
        label = _bucket_label(bucket_date)
        if rec.decision:
            buckets[label]['decision'].append(rec)
        if rec.outcome and rec.outcome.applied and rec.outcome.outcome_positive is not None:
            buckets[label]['evaluated'].append(rec)

    trend = []
    for label, group in buckets.items():
        decisions = group['decision']
        accepted = [item for item in decisions if item.decision and item.decision.accepted]
        evaluated = group['evaluated']
        positives = [item for item in evaluated if item.outcome and item.outcome.outcome_positive]
        trend.append(
            {
                'data_fim': label,
                'taxa_aceitacao': _round(_safe_ratio(len(accepted), len(decisions))),
                'taxa_eficacia': _round(_safe_ratio(len(positives), len(evaluated))),
            }
        )
    return trend


def _build_evidence(recommendations: Iterable[Recommendation]) -> dict:
    evaluated = [
        rec
        for rec in recommendations
        if rec.outcome and rec.outcome.applied and rec.outcome.outcome_positive is not None
    ]

    def to_item(rec: Recommendation) -> dict:
        return {
            'titulo': rec.title,
            'recomendacao': rec.recommendation_text,
            'confianca': _round(rec.confidence_ai, 2),
            'score': _round(rec.outcome.score_after if rec.outcome and rec.outcome.score_after is not None else rec.score_initial, 2),
        }

    acertos_alta = [to_item(rec) for rec in evaluated if rec.confidence_ai >= 0.8 and rec.outcome and rec.outcome.outcome_positive][:5]
    erros_alta = [to_item(rec) for rec in evaluated if rec.confidence_ai >= 0.8 and rec.outcome and not rec.outcome.outcome_positive][:5]
    acertos_baixa = [to_item(rec) for rec in evaluated if rec.confidence_ai < 0.5 and rec.outcome and rec.outcome.outcome_positive][:5]
    return {
        'acertos_alta_confianca': acertos_alta,
        'erros_alta_confianca': erros_alta,
        'acertos_baixa_confianca': acertos_baixa,
    }


def build_dashboard_metrics(db: Session, window_days: int) -> dict:
    recommendations = _iter_filtered_recommendations(db, window_days)
    decisions = [rec for rec in recommendations if rec.decision is not None]
    accepted = [rec for rec in decisions if rec.decision and rec.decision.accepted]
    evaluated = [
        rec for rec in accepted if rec.outcome and rec.outcome.applied and rec.outcome.outcome_positive is not None
    ]
    positives = [rec for rec in evaluated if rec.outcome and rec.outcome.outcome_positive]

    acceptance_rate = _safe_ratio(len(accepted), len(decisions))
    efficacy_rate = _safe_ratio(len(positives), len(evaluated))
    bins, ece, brier_score = _build_calibration_bins(recommendations)
    type_metrics = _build_type_metrics(recommendations)
    trend = _build_trend(recommendations)
    evidence = _build_evidence(recommendations)

    interpretation = (
        f'Com {len(recommendations)} recomendações na janela, a IA tem taxa de aceitação de '
        f'{acceptance_rate * 100:.1f}% e eficácia pós-correção de {efficacy_rate * 100:.1f}%.'
    )

    return {
        'janela_dias': window_days,
        'amostras_total': len(recommendations),
        'interpretacao_geral': interpretation,
        'metricas': {
            'taxa_aceitacao': {
                'valor': {
                    'taxa': _round(acceptance_rate),
                    'aceitas': len(accepted),
                    'total': len(decisions),
                }
            },
            'eficacia_pos_correcao': {
                'valor': {
                    'taxa': _round(efficacy_rate),
                    'sucessos': len(positives),
                    'avaliadas': len(evaluated),
                }
            },
            'calibracao': {
                'valor': {
                    'bins': bins,
                    'ece': ece,
                    'brier_score': brier_score,
                }
            },
            'por_tipo': {'valor': type_metrics},
            'tendencia_30d': {'valor': trend},
            'evidencias': {'valor': evidence},
        },
    }

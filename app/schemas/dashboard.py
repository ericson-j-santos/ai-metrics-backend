from typing import Any

from pydantic import BaseModel


class DashboardIAMetricasResponse(BaseModel):
    janela_dias: int
    amostras_total: int
    interpretacao_geral: str
    metricas: dict[str, Any]

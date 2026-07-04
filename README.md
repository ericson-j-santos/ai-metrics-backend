# AI Metrics Backend

Backend FastAPI para registrar recomendações de IA, decisões humanas, outcomes pós-implementação e consolidar métricas para o dashboard.

## Stack

- FastAPI
- SQLAlchemy 2
- SQLite para desenvolvimento local
- PostgreSQL para execução enterprise via Docker Compose
- Redis preparado para cache/fila em incrementos posteriores
- Pydantic v2
- Pytest
- Docker/Gunicorn/Uvicorn

## Endpoints

- `POST /v1/recomendacoes`
- `POST /v1/recomendacoes/{id}/decisao`
- `POST /v1/recomendacoes/{id}/outcome`
- `GET /v1/dashboard/ia?janela_dias=30`
- `GET /v1/incidentes?limit=20`
- `GET /v1/incidentes/{id}`
- `GET /health`
- `GET /live`
- `GET /ready`

## Como rodar em desenvolvimento

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8201
```

## Como rodar a foundation enterprise local

```bash
cp .env.example .env
export POSTGRES_PASSWORD='troque-esta-senha'
docker compose -f docker-compose.enterprise.yml up --build
```

Validações operacionais:

```bash
curl http://localhost:8201/health
curl http://localhost:8201/live
curl http://localhost:8201/ready
```

## Banco de dados

Por padrão usa SQLite local:

```env
DATABASE_URL=sqlite:///./ai_metrics.db
```

Para execução enterprise local com PostgreSQL:

```env
DATABASE_URL=postgresql+psycopg://ai_metrics:${POSTGRES_PASSWORD}@postgres:5432/ai_metrics
```

## Guard rails de produção

Quando `APP_ENV=production`, a aplicação bloqueia configurações inseguras:

- SQLite como banco de produção;
- `CORS_ORIGINS=*`;
- `LOG_LEVEL=DEBUG`;
- Swagger/OpenAPI exposto com `ENABLE_OPENAPI=true`;
- HTTPS desabilitado com `REQUIRE_HTTPS=false`.

## Exemplo de fluxo

### 1) Criar recomendação

```bash
curl -X POST http://localhost:8201/v1/recomendacoes \
  -H "Content-Type: application/json" \
  -d '{
    "id_incidente": 991,
    "titulo": "Cadastro / Salvar: CPF inválido",
    "tipo_recomendacao": "hotfix",
    "confianca_ia": 0.91,
    "recomendacao": "Aplicar validação de CPF no frontend e backend",
    "modelo": "gemini-2.5-flash",
    "score_inicial": 0.84
  }'
```

### 2) Registrar decisão

```bash
curl -X POST http://localhost:8201/v1/recomendacoes/1/decisao \
  -H "Content-Type: application/json" \
  -d '{
    "aceita": true,
    "motivo_decisao": "Falha recorrente em produção",
    "decidido_por": "ericsonjosedossantos@tieri659.onmicrosoft.com"
  }'
```

### 3) Registrar outcome

```bash
curl -X POST http://localhost:8201/v1/recomendacoes/1/outcome \
  -H "Content-Type: application/json" \
  -d '{
    "foi_aplicada": true,
    "versao_aplicada": "2.4.1",
    "outcome_positivo": true,
    "score_pos_correcao": 0.84,
    "observacao": "Queda de erro após deploy"
  }'
```

### 4) Ler dashboard

```bash
curl "http://localhost:8201/v1/dashboard/ia?janela_dias=30"
```

## Observações

- `POST /decisao` e `POST /outcome` funcionam como **upsert**: se já existir registro para a recomendação, ele é atualizado.
- O dashboard filtra a janela por `created_at` da recomendação.
- Para produção real, use banco gerenciado, secret manager, TLS no ingress/proxy e pipeline com gates de segurança.
- Detalhes da foundation aplicada: [`docs/enterprise-production-foundation.md`](docs/enterprise-production-foundation.md).

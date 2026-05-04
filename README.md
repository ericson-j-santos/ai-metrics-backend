# AI Metrics Backend

Backend FastAPI para registrar recomendações de IA, decisões humanas, outcomes pós-implementação e consolidar métricas para o dashboard.

## Stack

- FastAPI
- SQLAlchemy 2
- SQLite (dev)
- Pydantic v2
- Pytest

## Endpoints

- `POST /v1/recomendacoes`
- `POST /v1/recomendacoes/{id}/decisao`
- `POST /v1/recomendacoes/{id}/outcome`
- `GET /v1/dashboard/ia?janela_dias=30`
- `GET /health`

## Como rodar

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8201
```

## Banco de dados

Por padrão usa SQLite local:

```env
DATABASE_URL=sqlite:///./ai_metrics.db
```

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
- Para produção, troque SQLite por SQL Server e ajuste `DATABASE_URL`.

## Endpoints de incidentes

- `GET /v1/incidentes?limit=20`
- `GET /v1/incidentes/{id}`

Ao subir a aplicação em desenvolvimento, incidentes de exemplo são criados automaticamente se a base estiver vazia.

# Foundation Enterprise de Produção — AI Metrics Backend

## Objetivo

Este incremento transforma o backend FastAPI de uma base de desenvolvimento com SQLite para uma fundação operacional mais próxima de produção enterprise.

## Escopo aplicado

| Área | Implementação | Estado |
|---|---|---|
| Configuração | Variáveis versionadas e validação por ambiente | Verde |
| Banco | Pool configurável e PostgreSQL via `DATABASE_URL` | Verde |
| Runtime | Dockerfile com usuário não-root e healthcheck | Verde |
| Stack local enterprise | Docker Compose com API, PostgreSQL e Redis | Verde |
| Saúde operacional | `/health`, `/live` e `/ready` | Verde |
| Segurança básica | Bloqueios de produção para SQLite, wildcard CORS, OpenAPI e DEBUG | Verde |
| Documentação | Template `.env.example` e guia operacional | Verde |

## Como executar a stack enterprise local

```bash
cp .env.example .env
export POSTGRES_PASSWORD='troque-esta-senha'
docker compose -f docker-compose.enterprise.yml up --build
```

Endpoints de validação:

```bash
curl http://localhost:8201/health
curl http://localhost:8201/live
curl http://localhost:8201/ready
```

## Regras de produção aplicadas

Quando `APP_ENV=production`, a aplicação falha na inicialização se:

- `DATABASE_URL` usar SQLite;
- `CORS_ORIGINS` contiver `*`;
- `LOG_LEVEL` for `DEBUG`;
- `ENABLE_OPENAPI=true`;
- `REQUIRE_HTTPS=false`.

## Variáveis críticas

| Variável | Uso | Produção recomendada |
|---|---|---|
| `APP_ENV` | Ambiente lógico | `production` |
| `DATABASE_URL` | Banco transacional | PostgreSQL/SQL Server gerenciado |
| `CORS_ORIGINS` | Origens permitidas | Domínios oficiais, sem wildcard |
| `ENABLE_OPENAPI` | Exposição de Swagger/OpenAPI | `false` |
| `REQUIRE_HTTPS` | Redirecionamento HTTPS | `true` atrás de proxy compatível |
| `LOG_LEVEL` | Nível de log | `INFO` |

## Lacunas ainda não tratadas

| Item | Motivo | Próximo incremento recomendado |
|---|---|---|
| Migrações Alembic | Evitar mudança destrutiva sem inventário de modelos | Criar baseline Alembic |
| OIDC/RBAC real | Exige provedor corporativo | Integrar Azure AD/Keycloak |
| OpenTelemetry | Requer stack de coleta | Adicionar tracing e métricas |
| Filas/workers | Redis entrou como base, mas sem fila ativa | Criar worker assíncrono |
| Kubernetes/GitOps | Exige estratégia de ambiente | Criar manifests Helm/K8s |
| SAST/SBOM | Quality gate ainda básico | Adicionar pip-audit/Syft/Trivy |

## Decisão técnica

Este PR prioriza a fundação segura e reversível. Não altera contratos de endpoints existentes e preserva `/health` para compatibilidade.

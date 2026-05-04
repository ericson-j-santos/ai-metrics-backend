# Bundle Summary

## Atualização aplicada

- novo domínio de incidentes
- endpoints `GET /v1/incidentes` e `GET /v1/incidentes/{id}`
- seed automático de incidentes para desenvolvimento
- recomendação passa a persistir `contexto_incidente`
- compatibilidade SQLite para coluna nova em bases já criadas

## Fluxo suportado

1. Incidente é listado
2. Incidente é selecionado no frontend
3. Recomendação é criada vinculada ao incidente
4. Decisão e outcome são registrados
5. Dashboard consolida o histórico operacional

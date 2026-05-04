from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_list_incidents():
    response = client.get('/v1/incidentes?limit=5')
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_recommendation_flow():
    incidents = client.get('/v1/incidentes?limit=1').json()
    assert incidents
    incident = incidents[0]

    payload = {
        'id_incidente': incident['id'],
        'titulo': incident['titulo'],
        'contexto_incidente': 'Contexto de teste automatizado.',
        'tipo_recomendacao': 'hotfix',
        'confianca_ia': 0.91,
        'recomendacao': 'Aplicar validação imediata.',
        'modelo': 'gemini-2.5-flash',
        'score_inicial': 0.84,
    }
    created = client.post('/v1/recomendacoes', json=payload)
    assert created.status_code == 201
    recommendation_id = created.json()['id']

    decision = client.post(
        f'/v1/recomendacoes/{recommendation_id}/decisao',
        json={'aceita': True, 'motivo_decisao': 'Prioridade alta', 'decidido_por': 'ericsonjosedossantos@tieri659.onmicrosoft.com'},
    )
    assert decision.status_code == 200

    outcome = client.post(
        f'/v1/recomendacoes/{recommendation_id}/outcome',
        json={
            'foi_aplicada': True,
            'versao_aplicada': '9.9.9',
            'outcome_positivo': True,
            'score_pos_correcao': 0.9,
            'observacao': 'Teste automatizado',
        },
    )
    assert outcome.status_code == 200

    dashboard = client.get('/v1/dashboard/ia?janela_dias=30')
    assert dashboard.status_code == 200
    assert 'metricas' in dashboard.json()

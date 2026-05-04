from sqlalchemy import inspect, text
from sqlalchemy.orm import Session

from app.models.recommendation import Incident


def ensure_sqlite_compatibility(engine) -> None:
    if engine.dialect.name != 'sqlite':
        return

    inspector = inspect(engine)
    if 'recommendation_ia' in inspector.get_table_names():
        columns = {col['name'] for col in inspector.get_columns('recommendation_ia')}
        with engine.begin() as conn:
            if 'contexto_incidente' not in columns:
                conn.execute(text('ALTER TABLE recommendation_ia ADD COLUMN contexto_incidente TEXT'))


def seed_incidents(session: Session) -> None:
    has_incidents = session.query(Incident).first()
    if has_incidents:
        return

    incidents = [
        Incident(
            title='Cadastro / Salvar: CPF inválido passa sem bloqueio',
            module_name='Cadastro',
            functionality_name='Salvar cliente',
            severity='alta',
            status='aberto',
            current_score=0.84,
            context_summary='Clientes conseguem avançar no cadastro com CPF inválido quando a validação client-side falha. O backend não está rejeitando o payload em todos os cenários.',
            source_system='portal-clientes',
        ),
        Incident(
            title='Login / Auth: token expira sem renovação automática',
            module_name='Autenticação',
            functionality_name='Sessão do usuário',
            severity='alta',
            status='em_analise',
            current_score=0.79,
            context_summary='Usuários ativos por longos períodos perdem a sessão sem refresh token transparente. O erro aumenta em rotinas com várias abas abertas.',
            source_system='portal-clientes',
        ),
        Incident(
            title='Relatórios / Export: timeout em PDF grande',
            module_name='Relatórios',
            functionality_name='Exportar PDF',
            severity='media',
            status='aberto',
            current_score=0.52,
            context_summary='Exportações acima de 200 páginas retornam timeout entre 30 e 45 segundos. O usuário tenta novamente e gera duplicidade de processamento.',
            source_system='bi-reports',
        ),
        Incident(
            title='Dashboard / Filtro: data inválida quebra pesquisa',
            module_name='Dashboard',
            functionality_name='Filtro por período',
            severity='media',
            status='monitorando',
            current_score=0.41,
            context_summary='Datas fora do padrão DD/MM/AAAA ainda entram na query em alguns fluxos copiados do navegador, gerando erro intermitente.',
            source_system='analytics-hub',
        ),
    ]
    session.add_all(incidents)
    session.commit()

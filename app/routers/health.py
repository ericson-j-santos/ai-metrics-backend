from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db

router = APIRouter(tags=['health'])


@router.get('/health')
def health() -> dict:
    return {'status': 'ok'}


@router.get('/ready')
def readiness(db: Session = Depends(get_db)) -> dict:
    db.execute(text('SELECT 1'))
    settings = get_settings()
    return {
        'status': 'ready',
        'app': settings.app_name,
        'version': settings.app_version,
        'environment': settings.app_env,
        'dependencies': {
            'database': 'ok',
        },
    }


@router.get('/live')
def liveness() -> dict:
    settings = get_settings()
    return {
        'status': 'alive',
        'app': settings.app_name,
        'version': settings.app_version,
        'environment': settings.app_env,
    }

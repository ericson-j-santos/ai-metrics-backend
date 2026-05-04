from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.bootstrap import ensure_sqlite_compatibility, seed_incidents
from app.core.config import get_settings
from app.core.database import Base, SessionLocal, engine
from app.core.logging import configure_logging
from app.core.middleware import CorrelationIdMiddleware
from app.routers.dashboard import router as dashboard_router
from app.routers.health import router as health_router
from app.routers.incidents import router as incidents_router
from app.routers.recommendations import router as recommendations_router

settings = get_settings()
configure_logging(settings.log_level)


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    ensure_sqlite_compatibility(engine)
    with SessionLocal() as session:
        seed_incidents(session)
    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(health_router)
app.include_router(incidents_router)
app.include_router(recommendations_router)
app.include_router(dashboard_router)

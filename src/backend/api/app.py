"""FastAPI Application Factory.

Erstellt und konfiguriert die FastAPI-Anwendung
mit allen Routen und Middleware.
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from backend.config.settings import get_settings
from backend.core.database import dispose_engines, get_config_engine
from backend.core.services.database_service import DatabaseService

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Lifespan-Event fuer Startup und Shutdown.

    Initialisiert die Datenbank-Engine beim Start
    und schliesst sie beim Herunterfahren.
    """
    # Startup: Engine initialisieren
    get_config_engine()
    logger.info("Datenbank-Engine initialisiert")
    yield
    # Shutdown: Engines schliessen
    await dispose_engines()
    logger.info("Datenbank-Engines geschlossen")


def create_app() -> FastAPI:
    """Erstellt die FastAPI-Anwendung.

    Returns:
        Konfigurierte FastAPI-Instanz
    """
    settings = get_settings()

    app = FastAPI(
        title=settings.api.title,
        version=settings.api.version,
        debug=settings.api.debug,
        lifespan=lifespan,
    )

    _register_routes(app)

    return app


def _register_routes(app: FastAPI) -> None:
    """Registriert alle API-Routen.

    Args:
        app: FastAPI-Instanz
    """

    @app.get("/api/v1/health")
    async def health_check() -> JSONResponse:
        """Health-Check Endpoint fuer Monitoring."""
        db_ok = await DatabaseService.check_connection()
        status = "healthy" if db_ok else "degraded"
        return JSONResponse(
            content={
                "data": {
                    "status": status,
                    "database": "connected" if db_ok else "disconnected",
                },
                "error": None,
            }
        )

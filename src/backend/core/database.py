"""Datenbank-Engine und Session-Management.

Stellt Factory-Funktionen fuer SQLAlchemy Async-Engines
und Sessions bereit. Unterstuetzt die zentrale Config-DB
sowie dynamische Projekt-Datenbanken.
"""

from collections.abc import AsyncGenerator
from typing import Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from backend.config.settings import get_settings

# Cache fuer Engines (vermeidet mehrfache Engine-Erstellung)
_config_engine: Optional[AsyncEngine] = None
_project_engines: dict[str, AsyncEngine] = {}


def get_config_engine() -> AsyncEngine:
    """Erstellt oder gibt die gecachte Config-DB Engine zurueck.

    Returns:
        AsyncEngine fuer die zentrale Konfigurationsdatenbank
    """
    global _config_engine
    if _config_engine is None:
        settings = get_settings()
        _config_engine = create_async_engine(
            settings.database.async_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=10,
            max_overflow=20,
        )
    return _config_engine


def get_config_session_factory() -> async_sessionmaker[AsyncSession]:
    """Erstellt eine Session-Factory fuer die Config-DB.

    Returns:
        async_sessionmaker fuer Config-DB Sessions
    """
    engine = get_config_engine()
    return async_sessionmaker(engine, expire_on_commit=False)


def get_project_engine(db_name: str) -> AsyncEngine:
    """Erstellt oder gibt die gecachte Engine fuer eine Projekt-DB zurueck.

    Args:
        db_name: Name der Projekt-Datenbank

    Returns:
        AsyncEngine fuer die Projekt-Datenbank
    """
    if db_name not in _project_engines:
        settings = get_settings()
        project_url = (
            f"postgresql+asyncpg://{settings.database.user}:"
            f"{settings.database.password}@{settings.database.host}:"
            f"{settings.database.port}/{db_name}"
        )
        _project_engines[db_name] = create_async_engine(
            project_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            pool_size=5,
            max_overflow=10,
        )
    return _project_engines[db_name]


def get_project_session_factory(db_name: str) -> async_sessionmaker[AsyncSession]:
    """Erstellt eine Session-Factory fuer eine Projekt-DB.

    Args:
        db_name: Name der Projekt-Datenbank

    Returns:
        async_sessionmaker fuer Projekt-DB Sessions
    """
    engine = get_project_engine(db_name)
    return async_sessionmaker(engine, expire_on_commit=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI Dependency fuer Config-DB Sessions.

    Yields:
        AsyncSession fuer die Konfigurationsdatenbank
    """
    session_factory = get_config_session_factory()
    async with session_factory() as session:
        yield session


async def dispose_engines() -> None:
    """Schliesst alle Datenbank-Engines und gibt Ressourcen frei.

    Wird beim Herunterfahren der Anwendung aufgerufen.
    """
    global _config_engine
    if _config_engine is not None:
        await _config_engine.dispose()
        _config_engine = None

    for engine in _project_engines.values():
        await engine.dispose()
    _project_engines.clear()

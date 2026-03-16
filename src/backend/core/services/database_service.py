"""Service fuer die Verwaltung von Projekt-Datenbanken.

Erstellt und entfernt projektspezifische Datenbanken
und initialisiert deren Schema.
"""

import logging

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from backend.config.settings import get_settings
from backend.core.database import get_config_engine, get_project_engine
from backend.core.models.base import Base
from backend.core.models.project_db import CrawlRun, Issue, Link, Page  # noqa: F401

logger = logging.getLogger(__name__)


class DatabaseService:
    """Verwaltet die Erstellung und Loeschung von Projekt-Datenbanken.

    Jedes Projekt erhaelt eine eigene PostgreSQL-Datenbank
    mit der Naming-Convention 'seo_project_{project_id}'.
    """

    @staticmethod
    def get_project_db_name(project_id: int) -> str:
        """Generiert den Datenbanknamen fuer ein Projekt.

        Args:
            project_id: ID des Projekts

        Returns:
            Datenbankname im Format 'seo_project_{project_id}'
        """
        return f"seo_project_{project_id}"

    @staticmethod
    async def create_project_database(project_id: int) -> str:
        """Erstellt eine neue Datenbank fuer ein Projekt.

        Erstellt die Datenbank und initialisiert das Schema
        mit allen Projekt-Tabellen.

        Args:
            project_id: ID des Projekts

        Returns:
            Name der erstellten Datenbank

        Raises:
            RuntimeError: Wenn die Datenbank nicht erstellt werden konnte
        """
        db_name = DatabaseService.get_project_db_name(project_id)
        settings = get_settings()

        # Datenbank erstellen ueber eine Verbindung ohne Transaktion
        # (CREATE DATABASE kann nicht in einer Transaktion laufen)
        maintenance_url = (
            f"postgresql+asyncpg://{settings.database.user}:"
            f"{settings.database.password}@{settings.database.host}:"
            f"{settings.database.port}/postgres"
        )
        engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")

        try:
            async with engine.connect() as conn:
                # Pruefen ob Datenbank bereits existiert
                result = await conn.execute(
                    text("SELECT 1 FROM pg_database WHERE datname = :db_name"),
                    {"db_name": db_name},
                )
                if result.scalar() is not None:
                    logger.info("Datenbank '%s' existiert bereits", db_name)
                else:
                    await conn.execute(text(f'CREATE DATABASE "{db_name}"'))
                    logger.info("Datenbank '%s' erstellt", db_name)
        finally:
            await engine.dispose()

        # Schema initialisieren
        await DatabaseService.init_project_schema(db_name)

        return db_name

    @staticmethod
    async def init_project_schema(db_name: str) -> None:
        """Initialisiert das Schema einer Projekt-Datenbank.

        Erstellt alle Projekt-Tabellen (CrawlRun, Page, Link, Issue).

        Args:
            db_name: Name der Projekt-Datenbank
        """
        engine = get_project_engine(db_name)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Schema in Datenbank '%s' initialisiert", db_name)

    @staticmethod
    async def drop_project_database(project_id: int) -> None:
        """Loescht die Datenbank eines Projekts.

        ACHTUNG: Diese Operation ist nicht umkehrbar!

        Args:
            project_id: ID des Projekts

        Raises:
            RuntimeError: Wenn die Datenbank nicht geloescht werden konnte
        """
        db_name = DatabaseService.get_project_db_name(project_id)
        settings = get_settings()

        # Bestehende Engine fuer diese DB schliessen
        project_engine = get_project_engine(db_name)
        await project_engine.dispose()

        # Datenbank loeschen ueber Maintenance-Verbindung
        maintenance_url = (
            f"postgresql+asyncpg://{settings.database.user}:"
            f"{settings.database.password}@{settings.database.host}:"
            f"{settings.database.port}/postgres"
        )
        engine = create_async_engine(maintenance_url, isolation_level="AUTOCOMMIT")

        try:
            async with engine.connect() as conn:
                # Aktive Verbindungen trennen
                await conn.execute(
                    text(
                        "SELECT pg_terminate_backend(pid) "
                        "FROM pg_stat_activity "
                        "WHERE datname = :db_name AND pid <> pg_backend_pid()"
                    ),
                    {"db_name": db_name},
                )
                await conn.execute(text(f'DROP DATABASE IF EXISTS "{db_name}"'))
                logger.info("Datenbank '%s' geloescht", db_name)
        finally:
            await engine.dispose()

    @staticmethod
    async def check_connection() -> bool:
        """Prueft die Verbindung zur Config-Datenbank.

        Returns:
            True wenn die Verbindung erfolgreich ist
        """
        try:
            engine = get_config_engine()
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            return True
        except Exception:
            logger.exception("Datenbankverbindung fehlgeschlagen")
            return False

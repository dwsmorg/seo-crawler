"""Unit-Tests fuer das Datenbank-Modul.

Testet Engine/Session-Erstellung und URL-Patterns
ohne tatsaechliche Datenbankverbindung.
"""

from unittest.mock import patch

from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

import backend.core.database as db_module
from backend.core.database import (
    get_config_engine,
    get_config_session_factory,
    get_project_engine,
    get_project_session_factory,
)
from backend.core.services.database_service import DatabaseService


class TestConfigEngine:
    """Tests fuer die Config-DB Engine."""

    def setup_method(self) -> None:
        """Engine-Cache vor jedem Test zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()

    def test_creates_async_engine(self) -> None:
        """get_config_engine muss eine AsyncEngine zurueckgeben."""
        engine = get_config_engine()
        assert isinstance(engine, AsyncEngine)

    def test_engine_is_cached(self) -> None:
        """Gleiche Engine bei erneutem Aufruf zurueckgeben."""
        e1 = get_config_engine()
        e2 = get_config_engine()
        assert e1 is e2

    def test_engine_url_contains_asyncpg(self) -> None:
        """Engine-URL muss asyncpg-Treiber verwenden."""
        engine = get_config_engine()
        assert "asyncpg" in str(engine.url.drivername)

    def teardown_method(self) -> None:
        """Engine-Cache nach jedem Test zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()


class TestConfigSession:
    """Tests fuer die Config-DB Session-Factory."""

    def setup_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()

    def test_returns_session_factory(self) -> None:
        """get_config_session_factory muss async_sessionmaker zurueckgeben."""
        factory = get_config_session_factory()
        assert isinstance(factory, async_sessionmaker)

    def teardown_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()


class TestProjectEngine:
    """Tests fuer Projekt-DB Engines."""

    def setup_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()

    def test_creates_async_engine(self) -> None:
        """get_project_engine muss eine AsyncEngine zurueckgeben."""
        engine = get_project_engine("seo_project_1")
        assert isinstance(engine, AsyncEngine)

    def test_engine_is_cached_per_db(self) -> None:
        """Gleiche Engine bei gleichem DB-Namen zurueckgeben."""
        e1 = get_project_engine("seo_project_1")
        e2 = get_project_engine("seo_project_1")
        assert e1 is e2

    def test_different_engines_for_different_dbs(self) -> None:
        """Verschiedene Engines fuer verschiedene DB-Namen erstellen."""
        e1 = get_project_engine("seo_project_1")
        e2 = get_project_engine("seo_project_2")
        assert e1 is not e2

    def test_engine_url_contains_db_name(self) -> None:
        """Engine-URL muss den Datenbanknamen enthalten."""
        engine = get_project_engine("seo_project_42")
        assert "seo_project_42" in str(engine.url)

    def teardown_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()


class TestProjectSession:
    """Tests fuer Projekt-DB Session-Factories."""

    def setup_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()

    def test_returns_session_factory(self) -> None:
        """get_project_session_factory muss async_sessionmaker zurueckgeben."""
        factory = get_project_session_factory("seo_project_1")
        assert isinstance(factory, async_sessionmaker)

    def teardown_method(self) -> None:
        """Engine-Cache zuruecksetzen."""
        db_module._config_engine = None
        db_module._project_engines.clear()


class TestDatabaseService:
    """Tests fuer den DatabaseService."""

    def test_get_project_db_name(self) -> None:
        """DB-Name muss korrekt generiert werden."""
        assert DatabaseService.get_project_db_name(1) == "seo_project_1"
        assert DatabaseService.get_project_db_name(42) == "seo_project_42"
        assert DatabaseService.get_project_db_name(999) == "seo_project_999"

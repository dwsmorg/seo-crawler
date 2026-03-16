"""Unit-Tests fuer die Konfiguration.

Testet Settings-Defaults, URL-Generierung und die Factory-Funktion.
"""

from backend.config.settings import (
    ApiSettings,
    CrawlerSettings,
    DatabaseSettings,
    RedisSettings,
    Settings,
    get_settings,
)


class TestDatabaseSettings:
    """Tests fuer PostgreSQL-Einstellungen."""

    def test_default_values(self) -> None:
        """Standardwerte muessen korrekt gesetzt sein."""
        db = DatabaseSettings()
        assert db.host == "localhost"
        assert db.port == 5432
        assert db.user == "seo_crawler"
        assert db.db == "seo_crawler"

    def test_async_url(self) -> None:
        """Async-URL muss asyncpg-Treiber enthalten."""
        db = DatabaseSettings()
        assert db.async_url.startswith("postgresql+asyncpg://")
        assert "seo_crawler" in db.async_url

    def test_sync_url(self) -> None:
        """Sync-URL muss psycopg2-Treiber enthalten."""
        db = DatabaseSettings()
        assert db.sync_url.startswith("postgresql+psycopg2://")
        assert "seo_crawler" in db.sync_url


class TestRedisSettings:
    """Tests fuer Redis-Einstellungen."""

    def test_default_values(self) -> None:
        """Standardwerte muessen korrekt gesetzt sein."""
        redis = RedisSettings()
        assert redis.host == "localhost"
        assert redis.port == 6379
        assert redis.db == 0
        assert redis.password is None

    def test_url_without_password(self) -> None:
        """URL ohne Passwort darf kein Auth-Segment enthalten."""
        redis = RedisSettings()
        assert redis.url == "redis://localhost:6379/0"

    def test_url_with_password(self) -> None:
        """URL mit Passwort muss Auth-Segment enthalten."""
        redis = RedisSettings(password="geheim")
        assert redis.url == "redis://:geheim@localhost:6379/0"


class TestApiSettings:
    """Tests fuer API-Einstellungen."""

    def test_default_values(self) -> None:
        """Standardwerte muessen korrekt gesetzt sein."""
        api = ApiSettings()
        assert api.host == "0.0.0.0"
        assert api.port == 8000
        assert api.debug is False
        assert api.title == "SEO-Crawler API"


class TestCrawlerSettings:
    """Tests fuer Crawler-Einstellungen."""

    def test_default_values(self) -> None:
        """Standardwerte muessen korrekt gesetzt sein."""
        crawler = CrawlerSettings()
        assert crawler.max_depth == 10
        assert crawler.concurrent_requests == 16
        assert crawler.download_delay == 0.25
        assert crawler.autothrottle_enabled is True
        assert crawler.respect_robots_txt is True


class TestSettings:
    """Tests fuer die Hauptkonfiguration."""

    def test_contains_all_sub_settings(self) -> None:
        """Settings muss alle Teilkonfigurationen enthalten."""
        settings = Settings()
        assert isinstance(settings.database, DatabaseSettings)
        assert isinstance(settings.redis, RedisSettings)
        assert isinstance(settings.api, ApiSettings)
        assert isinstance(settings.crawler, CrawlerSettings)


class TestGetSettings:
    """Tests fuer die Factory-Funktion."""

    def test_returns_settings_instance(self) -> None:
        """Factory muss eine Settings-Instanz zurueckgeben."""
        get_settings.cache_clear()
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_caching(self) -> None:
        """Factory muss dieselbe Instanz zurueckgeben (Caching)."""
        get_settings.cache_clear()
        s1 = get_settings()
        s2 = get_settings()
        assert s1 is s2

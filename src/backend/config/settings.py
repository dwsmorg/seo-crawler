"""Zentrale Anwendungskonfiguration mit Pydantic Settings.

Laedt Umgebungsvariablen aus der .env-Datei und stellt
typisierte Konfigurationsobjekte bereit.
"""

from functools import lru_cache
from typing import Optional

from pydantic import computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """PostgreSQL-Datenbankeinstellungen."""

    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    host: str = "localhost"
    port: int = 5432
    user: str = "seo_crawler"
    password: str = "seo_crawler_dev"
    db: str = "seo_crawler"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def async_url(self) -> str:
        """Async-Verbindungs-URL fuer asyncpg/SQLAlchemy."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"

    @computed_field  # type: ignore[prop-decorator]
    @property
    def sync_url(self) -> str:
        """Synchrone Verbindungs-URL fuer psycopg2/Alembic."""
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db}"


class RedisSettings(BaseSettings):
    """Redis-Verbindungseinstellungen."""

    model_config = SettingsConfigDict(env_prefix="REDIS_")

    host: str = "localhost"
    port: int = 6379
    db: int = 0
    password: Optional[str] = None

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """Redis-Verbindungs-URL."""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class ApiSettings(BaseSettings):
    """FastAPI-Server-Einstellungen."""

    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    title: str = "SEO-Crawler API"
    version: str = "1.0.0"


class CrawlerSettings(BaseSettings):
    """Scrapy-Crawler-Einstellungen."""

    model_config = SettingsConfigDict(env_prefix="CRAWL_")

    max_depth: int = 10
    concurrent_requests: int = 16
    download_delay: float = 0.25
    autothrottle_enabled: bool = True
    respect_robots_txt: bool = True
    user_agent: str = "SEO-Crawler/1.0 (+https://github.com/dwsm/seo-crawler)"


class Settings(BaseSettings):
    """Hauptkonfiguration - buendelt alle Teilkonfigurationen."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    database: DatabaseSettings = DatabaseSettings()
    redis: RedisSettings = RedisSettings()
    api: ApiSettings = ApiSettings()
    crawler: CrawlerSettings = CrawlerSettings()


@lru_cache
def get_settings() -> Settings:
    """Factory-Funktion fuer gecachte Settings-Instanz.

    Returns:
        Singleton Settings-Objekt
    """
    return Settings()

"""Alembic Migration Environment.

Konfiguriert Alembic fuer die zentrale Config-Datenbank
mit automatischer URL-Aufloesung aus den Settings.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from backend.config.settings import get_settings
from backend.core.models.base import Base

# Alembic Config-Objekt
config = context.config

# Logging-Konfiguration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target Metadata fuer Auto-Migration
target_metadata = Base.metadata

# Datenbank-URL aus Settings laden
settings = get_settings()
config.set_main_option("sqlalchemy.url", settings.database.sync_url)


def run_migrations_offline() -> None:
    """Migrationen im Offline-Modus ausfuehren.

    Generiert SQL-Statements ohne Datenbankverbindung.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Migrationen im Online-Modus ausfuehren.

    Erstellt eine Engine-Verbindung und fuehrt Migrationen aus.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

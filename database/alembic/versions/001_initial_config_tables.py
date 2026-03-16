"""Initiale Config-DB Tabellen.

Revision ID: 001_initial
Revises: None
Create Date: 2026-03-16
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision-Identifier
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Erstellt alle Config-DB Tabellen und Default-Daten."""
    # Rollen-Tabelle
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(50), unique=True, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
    )

    # Benutzer-Tabelle
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(100), unique=True, nullable=False),
        sa.Column("email", sa.String(255), unique=True, nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column(
            "is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Projekte-Tabelle
    op.create_table(
        "projects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), unique=True, nullable=False),
        sa.Column("domain", sa.String(500), nullable=False),
        sa.Column(
            "status",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'active'"),
        ),
        sa.Column("db_name", sa.String(100), unique=True, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Crawl-Konfiguration
    op.create_table(
        "crawl_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column(
            "crawl_mode",
            sa.String(20),
            nullable=False,
            server_default=sa.text("'spider'"),
        ),
        sa.Column("start_urls", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column("allowed_domains", postgresql.ARRAY(sa.Text()), nullable=True),
        sa.Column(
            "max_depth", sa.Integer(), nullable=False, server_default=sa.text("10")
        ),
        sa.Column(
            "max_urls", sa.Integer(), nullable=False, server_default=sa.text("10000")
        ),
        sa.Column(
            "javascript_rendering",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("false"),
        ),
        sa.Column(
            "robots_txt_obey",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "download_delay",
            sa.Float(),
            nullable=False,
            server_default=sa.text("0.25"),
        ),
        sa.Column(
            "url_include_patterns", postgresql.ARRAY(sa.Text()), nullable=True
        ),
        sa.Column(
            "url_exclude_patterns", postgresql.ARRAY(sa.Text()), nullable=True
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
    )

    # Projekt-Berechtigungen
    op.create_table(
        "project_permissions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "project_id",
            sa.Integer(),
            sa.ForeignKey("projects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.Integer(),
            sa.ForeignKey("roles.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    # Default-Rollen einfuegen
    op.execute(
        "INSERT INTO roles (name, description) VALUES "
        "('admin', 'Vollzugriff auf alle Projektfunktionen'), "
        "('editor', 'Kann Crawls starten und Konfigurationen aendern'), "
        "('viewer', 'Nur Lesezugriff auf Crawl-Ergebnisse')"
    )

    # Default-Admin-User (Passwort muss bei erstem Login geaendert werden)
    op.execute(
        "INSERT INTO users (username, email, password_hash) VALUES "
        "('admin', 'admin@localhost', "
        "'$2b$12$placeholder_must_be_changed_on_first_login')"
    )


def downgrade() -> None:
    """Entfernt alle Config-DB Tabellen."""
    op.drop_table("project_permissions")
    op.drop_table("crawl_configs")
    op.drop_table("projects")
    op.drop_table("users")
    op.drop_table("roles")

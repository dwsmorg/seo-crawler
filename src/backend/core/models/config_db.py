"""Models fuer die zentrale Konfigurationsdatenbank.

Enthaelt Tabellen fuer Projekte, Crawl-Konfigurationen,
Benutzer, Rollen und Berechtigungen.
"""

from typing import Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.models.base import Base, TimestampMixin


class Project(TimestampMixin, Base):
    """Projekt-Model fuer die zentrale Verwaltung.

    Jedes Projekt repraesentiert eine zu crawlende Website
    und erhaelt eine eigene Datenbank.
    """

    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    domain: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="active"
    )
    db_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)

    crawl_config: Mapped[Optional["CrawlConfig"]] = relationship(
        back_populates="project", uselist=False, cascade="all, delete-orphan"
    )
    permissions: Mapped[list["ProjectPermission"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )


class CrawlConfig(TimestampMixin, Base):
    """Crawl-Konfiguration fuer ein Projekt.

    Definiert wie ein Projekt gecrawlt wird (Modus, Tiefe, Domains, etc.).
    """

    __tablename__ = "crawl_configs"

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), unique=True, nullable=False
    )

    crawl_mode: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="spider"
    )
    start_urls: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text), nullable=True)
    allowed_domains: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    max_depth: Mapped[int] = mapped_column(nullable=False, server_default="10")
    max_urls: Mapped[int] = mapped_column(nullable=False, server_default="10000")

    javascript_rendering: Mapped[bool] = mapped_column(
        nullable=False, server_default="false"
    )
    robots_txt_obey: Mapped[bool] = mapped_column(
        nullable=False, server_default="true"
    )
    download_delay: Mapped[float] = mapped_column(
        nullable=False, server_default="0.25"
    )

    url_include_patterns: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )
    url_exclude_patterns: Mapped[Optional[list[str]]] = mapped_column(
        ARRAY(Text), nullable=True
    )

    project: Mapped["Project"] = relationship(back_populates="crawl_config")


class User(TimestampMixin, Base):
    """Benutzer-Model fuer die Zugriffsverwaltung."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(nullable=False, server_default="true")

    permissions: Mapped[list["ProjectPermission"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class Role(Base):
    """Rollen-Model fuer die Berechtigungsverwaltung."""

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class ProjectPermission(Base):
    """Verknuepfung zwischen Projekt, Benutzer und Rolle.

    Definiert welche Rolle ein Benutzer in einem bestimmten Projekt hat.
    """

    __tablename__ = "project_permissions"
    __table_args__ = (
        UniqueConstraint("project_id", "user_id", name="uq_project_user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    role_id: Mapped[int] = mapped_column(
        ForeignKey("roles.id", ondelete="RESTRICT"), nullable=False
    )

    project: Mapped["Project"] = relationship(back_populates="permissions")
    user: Mapped["User"] = relationship(back_populates="permissions")
    role: Mapped["Role"] = relationship()

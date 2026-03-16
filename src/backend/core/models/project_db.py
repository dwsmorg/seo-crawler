"""Models fuer die projektspezifischen Datenbanken.

Jedes Projekt erhaelt eine eigene Datenbank mit diesen Tabellen
fuer Crawl-Durchlaeufe, Seiten, Links und Issues.
"""

from datetime import datetime
from typing import Any, Optional

from sqlalchemy import ForeignKey, Index, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.models.base import Base


class CrawlRun(Base):
    """Repraesentiert einen einzelnen Crawl-Durchlauf.

    Speichert Status, Statistiken und die zum Zeitpunkt des Crawls
    aktive Konfiguration als Snapshot.
    """

    __tablename__ = "crawl_runs"

    id: Mapped[int] = mapped_column(primary_key=True)
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="pending"
    )
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    urls_crawled: Mapped[int] = mapped_column(nullable=False, server_default="0")
    urls_total: Mapped[int] = mapped_column(nullable=False, server_default="0")
    errors_count: Mapped[int] = mapped_column(nullable=False, server_default="0")
    config_snapshot: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )
    statistics: Mapped[Optional[dict[str, Any]]] = mapped_column(
        JSONB, nullable=True
    )

    pages: Mapped[list["Page"]] = relationship(
        back_populates="crawl_run", cascade="all, delete-orphan"
    )
    links: Mapped[list["Link"]] = relationship(
        back_populates="crawl_run", cascade="all, delete-orphan"
    )
    issues: Mapped[list["Issue"]] = relationship(
        back_populates="crawl_run", cascade="all, delete-orphan"
    )


class Page(Base):
    """Repraesentiert eine gecrawlte Seite mit allen SEO-relevanten Daten."""

    __tablename__ = "pages"
    __table_args__ = (
        UniqueConstraint("crawl_run_id", "url", name="uq_crawl_run_url"),
        Index("ix_pages_status_code", "status_code"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    crawl_run_id: Mapped[int] = mapped_column(
        ForeignKey("crawl_runs.id", ondelete="CASCADE"), nullable=False
    )
    url: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[Optional[int]] = mapped_column(nullable=True)
    content_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    response_time_ms: Mapped[Optional[int]] = mapped_column(nullable=True)

    title: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meta_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    h1: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    canonical_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    robots_meta: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    hreflang: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(nullable=True)
    content_length: Mapped[Optional[int]] = mapped_column(nullable=True)
    crawled_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)

    crawl_run: Mapped["CrawlRun"] = relationship(back_populates="pages")
    issues: Mapped[list["Issue"]] = relationship(
        back_populates="page", cascade="all, delete-orphan"
    )


class Link(Base):
    """Repraesentiert einen Link zwischen zwei URLs."""

    __tablename__ = "links"
    __table_args__ = (
        UniqueConstraint(
            "crawl_run_id", "source_url", "target_url",
            name="uq_crawl_run_source_target",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    crawl_run_id: Mapped[int] = mapped_column(
        ForeignKey("crawl_runs.id", ondelete="CASCADE"), nullable=False
    )
    source_url: Mapped[str] = mapped_column(Text, nullable=False)
    target_url: Mapped[str] = mapped_column(Text, nullable=False)
    link_type: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="internal"
    )
    anchor_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_broken: Mapped[bool] = mapped_column(nullable=False, server_default="false")

    crawl_run: Mapped["CrawlRun"] = relationship(back_populates="links")


class Issue(Base):
    """Repraesentiert ein erkanntes SEO-Problem."""

    __tablename__ = "issues"

    id: Mapped[int] = mapped_column(primary_key=True)
    crawl_run_id: Mapped[int] = mapped_column(
        ForeignKey("crawl_runs.id", ondelete="CASCADE"), nullable=False
    )
    page_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("pages.id", ondelete="SET NULL"), nullable=True
    )
    issue_type: Mapped[str] = mapped_column(String(100), nullable=False)
    severity: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="info"
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    affected_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detected_at: Mapped[datetime] = mapped_column(
        nullable=False,
        server_default="now()",
    )

    crawl_run: Mapped["CrawlRun"] = relationship(back_populates="issues")
    page: Mapped[Optional["Page"]] = relationship(back_populates="issues")

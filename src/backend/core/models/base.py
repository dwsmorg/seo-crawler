"""Basis-Klassen fuer alle SQLAlchemy-Datenbankmodelle.

Stellt die Declarative Base und gemeinsame Mixins bereit.
"""

from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Gemeinsame Basis-Klasse fuer alle SQLAlchemy-Models."""

    pass


class TimestampMixin:
    """Mixin fuer automatische Zeitstempel-Felder.

    Fuegt created_at und updated_at mit Server-Defaults hinzu.
    """

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

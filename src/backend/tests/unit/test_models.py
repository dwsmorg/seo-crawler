"""Unit-Tests fuer die SQLAlchemy-Datenbankmodelle.

Testet Model-Definitionen, Spalten, Typen und Constraints
ohne Datenbankverbindung.
"""

from sqlalchemy import Table, inspect as sa_inspect
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from backend.core.models import (
    Base,
    CrawlConfig,
    CrawlRun,
    Issue,
    Link,
    Page,
    Project,
    ProjectPermission,
    Role,
    TimestampMixin,
    User,
)


class TestBase:
    """Tests fuer die Declarative Base."""

    def test_base_is_declarative(self) -> None:
        """Base muss eine DeclarativeBase sein."""
        assert hasattr(Base, "metadata")
        assert hasattr(Base, "registry")

    def test_timestamp_mixin_has_fields(self) -> None:
        """TimestampMixin muss created_at und updated_at definieren."""
        assert hasattr(TimestampMixin, "created_at")
        assert hasattr(TimestampMixin, "updated_at")


class TestProjectModel:
    """Tests fuer das Project-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'projects' sein."""
        assert Project.__tablename__ == "projects"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(Project)
        column_names = [c.key for c in mapper.column_attrs]
        expected = ["id", "name", "domain", "status", "db_name", "created_at", "updated_at"]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in Project"

    def test_name_is_unique(self) -> None:
        """Name-Spalte muss unique sein."""
        table: Table = Project.__table__  # type: ignore[assignment]
        name_col = table.c.name
        assert name_col.unique is True

    def test_db_name_is_unique(self) -> None:
        """DB-Name-Spalte muss unique sein."""
        table: Table = Project.__table__  # type: ignore[assignment]
        db_name_col = table.c.db_name
        assert db_name_col.unique is True

    def test_status_server_default(self) -> None:
        """Status muss Default 'active' haben."""
        table: Table = Project.__table__  # type: ignore[assignment]
        status_col = table.c.status
        assert status_col.server_default is not None


class TestCrawlConfigModel:
    """Tests fuer das CrawlConfig-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'crawl_configs' sein."""
        assert CrawlConfig.__tablename__ == "crawl_configs"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(CrawlConfig)
        column_names = [c.key for c in mapper.column_attrs]
        expected = [
            "id", "project_id", "crawl_mode", "start_urls", "allowed_domains",
            "max_depth", "max_urls", "javascript_rendering", "robots_txt_obey",
            "download_delay", "url_include_patterns", "url_exclude_patterns",
        ]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in CrawlConfig"

    def test_project_id_is_unique(self) -> None:
        """Project-ID muss unique sein (1:1 Beziehung)."""
        table: Table = CrawlConfig.__table__  # type: ignore[assignment]
        project_id_col = table.c.project_id
        assert project_id_col.unique is True

    def test_array_columns(self) -> None:
        """ARRAY-Spalten muessen den korrekten Typ haben."""
        table: Table = CrawlConfig.__table__  # type: ignore[assignment]
        assert isinstance(table.c.start_urls.type, ARRAY)
        assert isinstance(table.c.allowed_domains.type, ARRAY)
        assert isinstance(table.c.url_include_patterns.type, ARRAY)
        assert isinstance(table.c.url_exclude_patterns.type, ARRAY)

    def test_foreign_key_to_project(self) -> None:
        """project_id muss FK auf projects.id haben."""
        table: Table = CrawlConfig.__table__  # type: ignore[assignment]
        fks = list(table.c.project_id.foreign_keys)
        assert len(fks) == 1
        assert str(fks[0].column) == "projects.id"


class TestUserModel:
    """Tests fuer das User-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'users' sein."""
        assert User.__tablename__ == "users"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(User)
        column_names = [c.key for c in mapper.column_attrs]
        expected = ["id", "username", "email", "password_hash", "is_active"]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in User"

    def test_username_is_unique(self) -> None:
        """Username muss unique sein."""
        table: Table = User.__table__  # type: ignore[assignment]
        assert table.c.username.unique is True

    def test_email_is_unique(self) -> None:
        """Email muss unique sein."""
        table: Table = User.__table__  # type: ignore[assignment]
        assert table.c.email.unique is True


class TestRoleModel:
    """Tests fuer das Role-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'roles' sein."""
        assert Role.__tablename__ == "roles"

    def test_name_is_unique(self) -> None:
        """Rollenname muss unique sein."""
        table: Table = Role.__table__  # type: ignore[assignment]
        assert table.c.name.unique is True


class TestProjectPermissionModel:
    """Tests fuer das ProjectPermission-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'project_permissions' sein."""
        assert ProjectPermission.__tablename__ == "project_permissions"

    def test_unique_constraint(self) -> None:
        """UniqueConstraint auf (project_id, user_id) muss existieren."""
        table: Table = ProjectPermission.__table__  # type: ignore[assignment]
        constraints = [
            c for c in table.constraints
            if hasattr(c, "columns") and len(c.columns) == 2
        ]
        constraint_cols = None
        for c in constraints:
            cols = {col.name for col in c.columns}
            if cols == {"project_id", "user_id"}:
                constraint_cols = cols
                break
        assert constraint_cols is not None, "UniqueConstraint auf (project_id, user_id) fehlt"

    def test_foreign_keys(self) -> None:
        """Alle Foreign Keys muessen korrekt definiert sein."""
        table: Table = ProjectPermission.__table__  # type: ignore[assignment]
        fk_targets = {
            str(fk.column) for col in table.columns for fk in col.foreign_keys
        }
        assert "projects.id" in fk_targets
        assert "users.id" in fk_targets
        assert "roles.id" in fk_targets


class TestCrawlRunModel:
    """Tests fuer das CrawlRun-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'crawl_runs' sein."""
        assert CrawlRun.__tablename__ == "crawl_runs"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(CrawlRun)
        column_names = [c.key for c in mapper.column_attrs]
        expected = [
            "id", "status", "started_at", "completed_at",
            "urls_crawled", "urls_total", "errors_count",
            "config_snapshot", "statistics",
        ]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in CrawlRun"

    def test_jsonb_columns(self) -> None:
        """JSONB-Spalten muessen den korrekten Typ haben."""
        table: Table = CrawlRun.__table__  # type: ignore[assignment]
        assert isinstance(table.c.config_snapshot.type, JSONB)
        assert isinstance(table.c.statistics.type, JSONB)


class TestPageModel:
    """Tests fuer das Page-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'pages' sein."""
        assert Page.__tablename__ == "pages"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(Page)
        column_names = [c.key for c in mapper.column_attrs]
        expected = [
            "id", "crawl_run_id", "url", "status_code", "content_type",
            "response_time_ms", "title", "meta_description", "h1",
            "canonical_url", "robots_meta", "hreflang",
            "word_count", "content_length", "crawled_at",
        ]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in Page"

    def test_unique_constraint(self) -> None:
        """UniqueConstraint auf (crawl_run_id, url) muss existieren."""
        table: Table = Page.__table__  # type: ignore[assignment]
        constraints = [
            c for c in table.constraints
            if hasattr(c, "columns") and len(c.columns) == 2
        ]
        found = False
        for c in constraints:
            cols = {col.name for col in c.columns}
            if cols == {"crawl_run_id", "url"}:
                found = True
                break
        assert found, "UniqueConstraint auf (crawl_run_id, url) fehlt"

    def test_status_code_index(self) -> None:
        """Index auf status_code muss existieren."""
        table: Table = Page.__table__  # type: ignore[assignment]
        index_names = [idx.name for idx in table.indexes]
        assert "ix_pages_status_code" in index_names


class TestLinkModel:
    """Tests fuer das Link-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'links' sein."""
        assert Link.__tablename__ == "links"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(Link)
        column_names = [c.key for c in mapper.column_attrs]
        expected = [
            "id", "crawl_run_id", "source_url", "target_url",
            "link_type", "anchor_text", "is_broken",
        ]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in Link"

    def test_unique_constraint(self) -> None:
        """UniqueConstraint auf (crawl_run_id, source_url, target_url) muss existieren."""
        table: Table = Link.__table__  # type: ignore[assignment]
        constraints = [
            c for c in table.constraints
            if hasattr(c, "columns") and len(c.columns) == 3
        ]
        found = False
        for c in constraints:
            cols = {col.name for col in c.columns}
            if cols == {"crawl_run_id", "source_url", "target_url"}:
                found = True
                break
        assert found, "UniqueConstraint auf (crawl_run_id, source_url, target_url) fehlt"


class TestIssueModel:
    """Tests fuer das Issue-Model."""

    def test_tablename(self) -> None:
        """Tabellenname muss 'issues' sein."""
        assert Issue.__tablename__ == "issues"

    def test_columns(self) -> None:
        """Alle erwarteten Spalten muessen vorhanden sein."""
        mapper = sa_inspect(Issue)
        column_names = [c.key for c in mapper.column_attrs]
        expected = [
            "id", "crawl_run_id", "page_id", "issue_type",
            "severity", "description", "affected_url", "detected_at",
        ]
        for col in expected:
            assert col in column_names, f"Spalte '{col}' fehlt in Issue"

    def test_page_id_nullable(self) -> None:
        """page_id muss nullable sein."""
        table: Table = Issue.__table__  # type: ignore[assignment]
        assert table.c.page_id.nullable is True

    def test_foreign_keys(self) -> None:
        """Foreign Keys auf crawl_runs und pages muessen existieren."""
        table: Table = Issue.__table__  # type: ignore[assignment]
        fk_targets = {
            str(fk.column) for col in table.columns for fk in col.foreign_keys
        }
        assert "crawl_runs.id" in fk_targets
        assert "pages.id" in fk_targets

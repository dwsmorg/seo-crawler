# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).
## [1.0.7] - 16.03.2026

### Changed
- Projekt aufgeraeumt und Dokumentation aktualisiert
  - Verwaiste Artefakte entfernt (src/__init__.py, api/templates/, api/static/, Caches)
  - .env.example mit .env synchronisiert (Port 5436, pgAdmin)
  - docker-compose-local.yml: Alle Credentials in .env ausgelagert, pgAdmin mit Server-Config
  - project-structure.md vollstaendig aktualisiert auf aktuelle Struktur
  - CLAUDE.md: Docker-Container duerfen gestartet/gestoppt werden

### Files
- docs/ai-context/project-structure.md
- .env.example
- docker-compose-local.yml
- docker/pgadmin-servers.json
- CLAUDE.md
- .gitignore



## [1.0.6] - 16.03.2026

### Changed
- backend/ und frontend/ unter src/ zusammengefasst fuer klare Code-Trennung von Config/Infra/Doku
  - backend/ nach src/backend/ verschoben
  - frontend/ nach src/frontend/ verschoben
  - pyproject.toml: pythonpath und mypy_path auf 'src' gesetzt
  - Imports bleiben unveraendert (from backend.xxx)

### Files
- pyproject.toml
- database/alembic.ini



## [1.0.5] - 16.03.2026

### Changed
- Projektstruktur refactored: src/ zu backend/, Tests in backend/tests/, neue Ordner fuer frontend/, database/, docker/
  - src/ zu backend/ umbenannt - alle Imports angepasst
  - Tests von tests/ nach backend/tests/ verschoben
  - Alembic-Migrationen nach database/ verschoben
  - Neuer Ordner frontend/ mit templates/, static/, assets/, tests/
  - Neuer Ordner docker/ fuer Dockerfiles
  - Neuer Ordner database_data/ fuer persistente PostgreSQL-Daten (gitignored)
  - pyproject.toml, alembic.ini und Scrapy settings.py aktualisiert

### Files
- pyproject.toml
- .gitignore
- database/alembic.ini
- database/alembic/env.py
- backend/crawler/settings.py



## [1.0.4] - 16.03.2026

### Added
- Datenbank-Layer implementiert: SQLAlchemy Models, Database-Service und Alembic-Migrationen
  - SQLAlchemy Declarative Base mit TimestampMixin (created_at, updated_at)
  - Config-DB Models: Project, CrawlConfig, User, Role, ProjectPermission
  - Projekt-DB Models: CrawlRun, Page, Link, Issue mit JSONB/ARRAY-Feldern
  - Async Database Engine und Session Management mit Connection Pooling
  - DatabaseService fuer Multi-DB Verwaltung (CREATE/DROP Projekt-Datenbanken)
  - Alembic Setup mit initialer Migration und Default-Rollen/Admin-User
  - FastAPI Lifespan-Events fuer DB-Engine Startup/Shutdown
  - Health-Check Endpoint um DB-Connectivity erweitert
  - 45 neue Unit-Tests fuer Models, Database und DatabaseService

### Files
- src/core/models/base.py
- src/core/models/config_db.py
- src/core/models/project_db.py
- src/core/models/__init__.py
- src/core/database.py
- src/core/services/database_service.py
- alembic.ini
- alembic/env.py
- alembic/script.py.mako
- alembic/versions/001_initial_config_tables.py
- src/api/app.py
- tests/unit/test_models.py
- tests/unit/test_database.py



## [1.0.3] - 16.03.2026

### Added
- Projekt-Grundgeruest mit kompletter Code-Infrastruktur erstellt
  - pyproject.toml mit allen Dependencies (Scrapy, FastAPI, SQLAlchemy, Redis, etc.) und Dev-Tools (pytest, mypy, ruff, black)
  - Komplette Verzeichnisstruktur: src/crawler, src/api, src/core, src/analysis, src/config, tests/ mit __init__.py Dateien
  - src/config/settings.py - Pydantic BaseSettings mit DatabaseSettings, RedisSettings, ApiSettings, CrawlerSettings
  - src/api/app.py - FastAPI App-Factory mit Health-Check Endpoint /api/v1/health
  - src/crawler/settings.py - Scrapy-Konfiguration mit AutoThrottle und Playwright vorbereitet
  - src/crawler/items.py - PageItem Datenstruktur fuer gecrawlte Seiten
  - Docker-Setup: api.Dockerfile, crawler.Dockerfile, docker-compose-local/staging/prod.yml
  - .env.example - Template fuer alle Umgebungsvariablen
  - tests/unit/test_config.py - 11 Unit-Tests fuer Settings (alle bestanden)
  - Screaming Frog SEO Spider Verweise aus allen Dateien entfernt

### Files
- pyproject.toml
- .env.example
- src/config/settings.py
- src/api/app.py
- src/crawler/settings.py
- src/crawler/items.py
- docker/api.Dockerfile
- docker/crawler.Dockerfile
- docker-compose-local.yml
- docker-compose-staging.yml
- docker-compose-prod.yml
- tests/conftest.py
- tests/unit/test_config.py



## [1.0.2] - 16.03.2026

### Security
- CLAUDE.md, MCP-ASSISTANT-RULES.md und docs/ aus Git-Tracking entfernt
  - AI-Kontext-Dateien (CLAUDE.md, MCP-ASSISTANT-RULES.md) in .gitignore aufgenommen
  - docs/ Verzeichnis (AI-Dokumentation) in .gitignore aufgenommen
  - Alle Dateien bleiben lokal erhalten, sind aber nicht mehr im oeffentlichen Repository

### Files
- .gitignore



## [1.0.1] - 16.03.2026

### Security
- Sensible Dateien aus Git-Tracking entfernt und in .gitignore aufgenommen
  - .mcp.json (lokale MCP-Konfiguration mit Systempfaden) aus Git entfernt
  - .claude/ (lokale Claude Code Konfiguration, Hooks, Sounds) aus Git entfernt
  - .gitignore um .mcp.json und .claude/ erweitert

### Files
- .gitignore
- .mcp.json
- .claude/



## [1.0.0] - 16.03.2026

### Changed
- CLAUDE.md umstrukturiert und erweitert: Neue Gliederung mit Quick Start, Unit-Test-Pflicht, .env-Referenz, Projektwebseite und README-Hinweis
  - CLAUDE.md: Neue Nummerierung (Quick Start & Grundlagen als Sektion 1, Code-Index als Sektion 2)
  - Unit-Tests mit pytest als Pflicht fuer alle Methoden und Funktionen aufgenommen
  - .env als zentrale Ablage fuer Secrets und Konfigurationsdaten dokumentiert
  - Projektwebseite (documentation/webseite/) mit Tabler 1.3.0 als Marketing-Page und Online-Handbuch definiert
  - README.md im Root fuer GitHub erstellt mit Projektbeschreibung, Tech-Stack und Architektur
  - Bugfix subagent-context-injector.sh: Pfad docs/CLAUDE.md korrigiert zu CLAUDE.md
  - project-structure.md: README.md, .env und documentation/webseite/ im Dateibaum ergaenzt
  - docs-overview.md: README.md in Referenz-Dokumentation aufgenommen

### Files
- CLAUDE.md
- README.md
- .claude/hooks/subagent-context-injector.sh
- docs/ai-context/project-structure.md
- docs/ai-context/docs-overview.md




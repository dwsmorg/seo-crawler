# SEO Crawler Framework

Hochperformanter, modularer Web-Crawler fuer technische SEO-Audits.
Single Source of Truth fuer technische Website-Daten.

## Vision

Ein vollstaendig dockerisiertes SEO-Analyse-Tool, das Websites systematisch crawlt, technische SEO-Daten erfasst und ueber eine API sowie ein Web-Dashboard zugaenglich macht.

## Tech-Stack

| Komponente | Technologie |
|---|---|
| Crawler-Engine | Scrapy |
| API | FastAPI |
| Datenbank | PostgreSQL |
| Queue / Cache | Redis |
| Frontend | Tabler 1.3.0 (Bootstrap) |
| Containerisierung | Docker / Docker Compose |
| Sprache | Python 3.x |

## Architektur

Das Framework folgt einer Pipeline-Architektur mit klar getrennten Layern:

```
Ingestion (Scrapy) -> Queue (Redis) -> Storage (PostgreSQL) -> API (FastAPI) -> Dashboard
```

- **Ingestion Layer:** Scrapy-basierter Crawler fuer die Datenerfassung
- **Queue Layer:** Redis fuer Job-Management und Caching
- **Storage Layer:** PostgreSQL fuer persistente Datenhaltung
- **API Layer:** FastAPI mit versionierten RESTful Endpoints
- **Analysis Layer:** SEO-Analyse und Reporting

## Projektstruktur

```
seo-crawler/
├── docs/                          # AI-Kontext und Projektdokumentation
│   └── ai-context/               # Strukturierte AI-Dokumentation
├── documentation/
│   ├── changelog/                 # Versioniertes Changelog (MCP-verwaltet)
│   ├── design/                    # UI/UX Design-Basis (Tabler 1.3.0)
│   ├── git/                       # Git-Workflow-Scripts
│   └── webseite/                  # Projektwebseite (Marketing + Handbuch)
├── .claude/                       # Claude Code Konfiguration und Hooks
├── .env                           # Konfiguration und Secrets (nicht im Repo)
├── CLAUDE.md                      # AI-Kontext und Coding-Standards
└── README.md
```

## Entwicklungsstrategie

- **MVP-first:** Kernfunktionalitaet zuerst, schrittweise Erweiterung
- **API-first Design:** Backend-API als Grundlage, Dashboard als Konsument
- **Phasenweise Erweiterung:** Modularer Aufbau fuer kontrolliertes Wachstum

## Status

**Aktuelle Phase:** Pre-Development / Projektsetup

## Voraussetzungen

- Docker & Docker Compose
- Python 3.x
- Node.js (fuer Build-Tools)

## Installation

```bash
# Repository klonen
git clone https://github.com/dwsm/seo-crawler.git
cd seo-crawler

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env mit eigenen Werten befuellen

# Container starten
docker compose up -d
```

> Detaillierte Installationsanweisungen folgen mit dem MVP-Release.

## Lizenz

Folgt.

## Mitwirken

Dieses Projekt befindet sich in aktiver Entwicklung. Beitraege sind willkommen, sobald die Grundstruktur steht.

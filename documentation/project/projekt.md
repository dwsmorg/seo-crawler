# Projekt: „SEO-Crawler-Framework"

## 1. Vision & Zielsetzung

Entwicklung eines hochperformanten, modularen Web-Crawlers fuer technische SEO-Audits. Das System dient als Single Source of Truth fuer technische Website-Daten. Es ist darauf ausgelegt, Millionen von URLs zu verarbeiten, die Linkstruktur abzubilden und technische SEO-Fehler automatisiert zu identifizieren.

**Kernvorteile:**
- Daten-Souveraenitaet: Eigene PostgreSQL-Datenbank
- Skalierung: Server-basiert, horizontal skalierbar
- SQL-Analyse: Direkte Abfragen ohne Export-Workflows
- Erweiterbarkeit: Eigene Spider/Pipelines und offene Architektur
- API-first: Programmatischer Zugang zu allen Daten

## 2. Technische Architektur

### 2.1 Systemuebersicht

Dockerisiertes Multi-Container-System mit Pipeline-Architektur:

```
docker-compose-{local,staging,prod}.yml
├── postgres          Config-DB + Projekt-DBs
├── redis             Queue, Crawl-Status, Caching, Pub/Sub
├── crawler-worker    Scrapy + Playwright (horizontal skalierbar)
├── api               FastAPI (REST-API + Web-Dashboard)
└── scheduler         Cron/Event-Trigger (spaeter)
```

### 2.2 Layer-Architektur

**Ingestion Layer (Scrapy):** Asynchrones, paralleles Crawling mit AutoThrottle und Concurrency. Integration von scrapy-playwright fuer JavaScript-Rendering. Proxy-Rotation ueber Middleware.

**Queue Layer (Redis):** URL-Frontier fuer Crawl-Jobs, Live-Status und Fortschritts-Tracking, Deduplizierung bei mehreren Workern, Pub/Sub fuer Echtzeit-Updates ans Dashboard.

**Storage Layer (PostgreSQL):** Zentrale Config-DB fuer Projektverwaltung. Separate Datenbank pro Projekt fuer Crawl-Daten. Ermoeglicht saubere Isolation, unabhaengiges Backup/Restore und einfaches Loeschen von Projekten.

**API Layer (FastAPI):** REST-API fuer programmatischen Zugang zu allen Daten. Web-Dashboard mit Tabler UI, HTMX und Jinja2 Templates. Crawl-Steuerung (Start, Stop, Status).

**Analysis Layer:** SQL-basierte Auswertung innerhalb der Datenbank. Issue-Engine zur automatischen Erkennung von SEO-Defiziten.

## 3. Datenbank-Architektur

### 3.1 Config-DB (eine zentrale Instanz)

Verwaltung aller Projekte, Konfigurationen und Benutzer:

- **projects** — Projekt-Definitionen (Name, Domain, Einstellungen, Erstellungsdatum)
- **crawl_configs** — Crawl-Konfiguration pro Projekt (Modus, Limits, Rendering, Filtering)
- **users** — Benutzer-Konten (vorbereitet fuer Multi-User, Start mit Single-User)
- **roles** — Rollen-Definitionen (Admin, Viewer etc.)
- **project_permissions** — Zuordnung User <-> Projekt <-> Rolle
- **schedules** — Crawl-Zeitplaene pro Projekt (fuer Cron-Modus, spaeter)

### 3.2 Projekt-DBs (eine pro Projekt)

Isolierte Datenbank pro Projekt fuer Crawl-Daten:

- **crawl_runs** — Crawl-Durchlaeufe (ID, Start/Ende, Status, Statistiken, Konfiguration-Snapshot)
- **pages** — URL-Daten, Statuscodes, Ladezeiten, extrahierte Metadaten (Title, Description, Robots, Canonicals, Hreflang, H1-H6)
- **links** — Link-Beziehungen (source_url -> target_url, Typ: intern/extern, Ankertext)
- **issues** — Technische Befunde mit Severity (Broken Links, Redirect-Chains, Duplicate Content etc.)

Alle Datentabellen referenzieren eine `crawl_run_id` fuer historische Snapshots.

## 4. Crawl-Modi

**Spider-Modus (Standard):** Start-URL(s), dann allen internen Links folgen. Klassisches Crawling zur Erfassung der gesamten Seitenstruktur.

**List-Modus:** Feste URL-Liste uebergeben (CSV, API). Nur diese URLs crawlen, keinen Links folgen. Fuer Monitoring bestimmter Seiten oder Recheck nach Fixes.

**Sitemap-Modus:** URLs aus sitemap.xml lesen und crawlen. Optional: Links folgen ja/nein. Fuer Sitemap-Validierung und Index-Abgleich.

**Kombinationen:** Sitemap oder URL-Liste als Seed + Spider-Modus (Links folgen) fuer maximale Abdeckung.

## 5. Crawl-Konfiguration

Pro Projekt konfigurierbar:

### Basis
- Start-URL / Seed-URLs
- Crawl-Modus (Spider, List, Sitemap, Kombination)
- Erlaubte Domains (Scope)
- Max. Crawl-Tiefe
- Max. Anzahl URLs
- Crawl-Geschwindigkeit (Requests/Sekunde, AutoThrottle)

### Rendering
- JavaScript-Rendering an/aus
- Rendering-Timeout
- Viewport-Groesse (fuer responsive Seiten)

### Extraktion
- Meta-Tags, Headings, Images, Structured Data
- Custom Extraction Rules (CSS-Selektoren / XPath)
- robots.txt respektieren ja/nein

### Filtering
- URL-Pattern Include/Exclude (Regex)
- Dateitypen ignorieren (PDF, Images etc.)
- Query-Parameter Handling (ignorieren, normalisieren)

### Proxy
- Proxy-Rotation (Liste von Proxies)
- Pro Worker oder global konfigurierbar

## 6. Feature-Set

### 6.1 MVP (Phase 1)

**Technisches Crawling:** Systematische Erfassung von HTTP-Statuscodes, Meta-Tags (Title, Description, Robots), H1-H6-Hierarchien, Canonical-Tags, Hreflang-Attributen.

**JavaScript-Rendering:** Integration von Playwright via scrapy-playwright zur Verarbeitung dynamischer Inhalte (SPAs) und Extraktion von client-seitig generiertem DOM-Content. Konfigurierbar pro Projekt (an/aus).

**Link-Graph-Mapping:** Vollstaendiger Graph aus internen und externen Links zur Identifizierung von Orphan Pages und Analyse der Link-Struktur.

**Multi-Projekt-Verwaltung:** Projekte ueber API erstellen/verwalten. Jedes Projekt erhaelt automatisch eine eigene Datenbank. Individuelle Crawl-Konfiguration pro Projekt.

**Crawl-Runs mit Historie:** Mehrere Snapshots pro Projekt. Vergleichbarkeit ueber Zeit. Konfigurierbare Retention (Max. Anzahl Runs, aeltere automatisch loeschen/archivieren).

**Issue-Engine:** Automatische Erkennung von SEO-Defiziten mit Severity-Levels (Critical, Warning, Info):
- Broken Links (4xx, 5xx)
- Redirect-Chains und Redirect-Loops
- Missing/Duplicate Titles und Descriptions
- Missing H1, Multiple H1
- Missing Canonical, Canonical-Konflikte
- Duplicate Content
- Mixed Content (HTTP auf HTTPS-Seiten)
- Orphan Pages (nicht verlinkt)
- Tiefe Crawl-Tiefe (schwer erreichbare Seiten)
- Langsame Ladezeiten

**Crawl-Monitoring:** Live-Status eines laufenden Crawls (gecrawlte URLs, Fehler, Speed). Echtzeit-Updates via SSE (Server-Sent Events) ueber Redis Pub/Sub. Crawl abbrechen moeglich.

**REST-API:** Vollstaendiger API-Zugang zu allen Daten (Projekte, Crawl-Runs, Pages, Links, Issues). JSON-Responses. API-Versionierung (/v1/).

**Web-Dashboard:** FastAPI mit Jinja2 Templates. Tabler 1.3.0 als UI-Framework (Bootstrap 5). HTMX fuer dynamische Interaktionen. jQuery DataTables fuer Tabellen (AJAX, Search, Sort, Pagination). Tabler Icons (SVG inline).

**Manueller Crawl-Start:** Crawl per API-Call oder Dashboard-Button starten.

### 6.2 Phase 2

**Crawl-Scheduling:** Zeitgesteuerte Crawls per Cron-Konfiguration pro Projekt (z.B. "jeden Montag 3 Uhr"). Eigener Scheduler-Container.

**Event-basierte Trigger:** Webhook-Endpoints zum Ausloesen von Crawls (z.B. nach Deployment via CI/CD).

**Crawl-Run-Vergleich (Diff):** Diff zwischen zwei Runs (neue 404er, behobene Issues, neue/verschwundene Seiten). Trend-Daten (Issues ueber Zeit).

**Worker-Skalierung:** Mehrere Crawler-Container parallel. Job-Verteilung ueber Redis Queue. Jeder Worker mit eigenem Proxy moeglich.

**Custom Issue-Regeln:** Benutzerdefinierte Pruefregeln per Konfiguration.

### 6.3 Spaeter

**Multi-User mit Rollen:** Login-Flow, Session-Management. Rollen (Admin, Viewer) mit Projekt-Berechtigungen. Infrastruktur von Anfang an vorbereitet (DB-Schema, Auth-Middleware).

**Export-Formate:** CSV-Download fuer Pages, Links, Issues. PDF-Reports mit Zusammenfassung und Charts.

**Link-Graph-Visualisierung:** Interaktive Darstellung der Seitenstruktur.

## 7. Tech-Stack

| Komponente | Technologie |
|---|---|
| Crawling | Scrapy (Python) |
| JS-Rendering | Playwright via scrapy-playwright |
| API & Dashboard | FastAPI, Jinja2, HTMX |
| UI-Framework | Tabler 1.3.0 (Bootstrap 5) |
| Tabellen | jQuery DataTables (AJAX) |
| Icons | Tabler Icons (SVG) |
| Datenbank | PostgreSQL |
| Queue & Cache | Redis |
| Containerisierung | Docker, Docker Compose |
| Scheduling | APScheduler oder Celery Beat (Phase 2) |

## 8. Auth-Konzept

Von Anfang an vorbereitet, aber stufenweise aktiviert:

**Start (MVP):** Kein Login. Auth-Middleware ist implementiert, laesst aber alle Requests mit einem Default-User durch.

**Spaeter:** Middleware wird "scharf geschaltet". Login-Flow, Session-Management, Rollen-basierte Zugriffskontrolle pro Projekt.

Das DB-Schema (users, roles, project_permissions) existiert von Tag 1.

## 9. Strategischer Vorteil

**Daten-Souveraenitaet:** Volle Kontrolle ueber Rohdaten (inkl. HTML-Content) ohne Abhaengigkeit von Drittanbieter-Tools.

**Performance:** Schnelle technische Audits mittels optimierter SQL-Abfragen auf indizierten Tabellen.

**Flexibilitaet:** Erweiterbarkeit durch SQL-gestuetzte Logik und eigene Spider/Pipelines.

**Skalierbarkeit:** Server-basiert, Docker-skalierbar, keine RAM-Limitierung wie bei Desktop-Tools.

**API-first:** Alle Daten programmatisch zugaenglich fuer Automatisierung und Integration.

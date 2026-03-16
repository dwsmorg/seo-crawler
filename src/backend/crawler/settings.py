"""Scrapy-Konfiguration fuer den SEO-Crawler.

Standard-Einstellungen fuer das Crawling-Verhalten.
Werte koennen ueber die zentrale Settings-Klasse ueberschrieben werden.
"""

# Grundeinstellungen
BOT_NAME = "seo_crawler"
SPIDER_MODULES = ["backend.crawler.spiders"]
NEWSPIDER_MODULE = "backend.crawler.spiders"

# Hoefliches Crawling
ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 16
DOWNLOAD_DELAY = 0.25

# AutoThrottle
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 1.0
AUTOTHROTTLE_MAX_DELAY = 10.0
AUTOTHROTTLE_TARGET_CONCURRENCY = 8.0

# Caching
HTTPCACHE_ENABLED = False

# Pipelines (werden bei Bedarf aktiviert)
ITEM_PIPELINES: dict[str, int] = {}

# Middlewares (werden bei Bedarf aktiviert)
DOWNLOADER_MIDDLEWARES: dict[str, int] = {}

# Playwright-Integration (auskommentiert bis benoetigt)
# DOWNLOAD_HANDLERS = {
#     "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
#     "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
# }
# TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
# PLAYWRIGHT_BROWSER_TYPE = "chromium"
# PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}

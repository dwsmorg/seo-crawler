"""Scrapy Item-Definitionen fuer gecrawlte Daten.

Definiert die Datenstrukturen fuer die Pipeline-Verarbeitung.
Items werden in spaeteren Phasen erweitert.
"""

import scrapy


class PageItem(scrapy.Item):
    """Basis-Item fuer gecrawlte Seiten."""

    url = scrapy.Field()
    status_code = scrapy.Field()
    content_type = scrapy.Field()
    title = scrapy.Field()
    meta_description = scrapy.Field()
    canonical_url = scrapy.Field()
    crawl_timestamp = scrapy.Field()

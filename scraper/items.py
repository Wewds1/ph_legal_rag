import scrapy

class RawCaseItem(scrapy.Item):
    source = scrapy.Field()
    source_url = scrapy.Field()
    fetched_at = scrapy.Field()
    http_status = scrapy.Field()
    title_raw = scrapy.Field()
    html = scrapy.Field()
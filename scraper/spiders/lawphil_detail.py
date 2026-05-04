from datetime import datetime, UTC
import scrapy
from scraper.items import RawCaseItem


class LawphilDetailSpider(scrapy.Spider):
    name = "lawphil_detail"
    allowed_domains = ["lawphil.net"]

    start_urls = [
        # replace with real detail URLs during testing
    ]

    def parse(self, response):
        item = RawCaseItem()
        item["source"] = "lawphil"
        item["source_url"] = response.url
        item["fetched_at"] = datetime.now(UTC).isoformat()
        item["http_status"] = response.status
        item["title_raw"] = response.css("title::text").get()
        item["html"] = response.text
        yield item
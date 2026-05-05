from datetime import datetime, UTC
from pathlib import Path
import scrapy
from scraper.items import RawCaseItem


class LawphilDetailSpider(scrapy.Spider):
    name = "lawphil_detail"
    allowed_domains = ["lawphil.net"]

    def start_requests(self):
        links_file = Path("scraper/spiders/links/lawphil_links.txt")
        with open(links_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and line.startswith("http"):
                    yield scrapy.Request(line, callback=self.parse)

    def parse(self, response):
        item = RawCaseItem()
        item["source"] = "lawphil"
        item["source_url"] = response.url
        item["fetched_at"] = datetime.now(UTC).isoformat()
        item["http_status"] = response.status
        item["title_raw"] = response.css("title::text").get()
        item["html"] = response.text
        yield item
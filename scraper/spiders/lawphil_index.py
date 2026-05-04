import scrapy


class LawphilIndexSpider(scrapy.Spider):
    name = "lawphil_index"
    allowed_domains = ["lawphil.net"]
    start_urls = [
        "https://lawphil.net/judjuris/juri2024.html",
    ]

    def parse(self, response):
        links = response.css("a::attr(href)").getall()
        for href in links:
            if "/judjuris/" in href and href.endswith(".html"):
                yield response.follow(href, callback=self.parse_detail)

    def parse_detail(self, response):
        yield {
            "url": response.url,
        }
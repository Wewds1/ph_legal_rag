BOT_NAME = "legal_rag"

SPIDER_MODULES = ["scraper.spiders"]
NEWSPIDER_MODULE = "scraper.spiders"

ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 2
CONCURRENT_REQUESTS = 4
RETRY_TIMES = 3

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 10

USER_AGENT = "legal-rag-research-bot/1.0"

ITEM_PIPELINES = {
    "scraper.pipelines.RawHtmlPipeline": 300,
}
from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = 'book_scraper'

SPIDER_MODULES = ['book_scraper.spiders']
NEWSPIDER_MODULE = 'book_scraper.spiders'

# Crawl responsibly by identifying yourself
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure item pipelines
ITEM_PIPELINES = {
    'book_scraper.pipelines.MongoDBPipeline': 300,
}

# MongoDB settings
MONGODB_URI = getenv('MONGODB_URI', 'mongodb://localhost:27017')
MONGODB_DATABASE = getenv('MONGODB_DATABASE', 'books_db')
MONGODB_COLLECTION = getenv('MONGODB_COLLECTION', 'books')

# Configure maximum concurrent requests
CONCURRENT_REQUESTS = 1

# Configure a delay for requests
DOWNLOAD_DELAY = 2
RANDOMIZE_DOWNLOAD_DELAY = True

# Enable Splash middleware
SPLASH_URL = 'http://localhost:8050'

DOWNLOADER_MIDDLEWARES = {
    'scrapy_splash.SplashCookiesMiddleware': 723,
    'scrapy_splash.SplashMiddleware': 725,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100,
}

DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'
HTTPCACHE_STORAGE = 'scrapy_splash.SplashAwareFSCacheStorage'

# Add localhost to allowed domains
ALLOWED_DOMAINS = ['chitai-gorod.ru', 'localhost'] 
from os import getenv
from dotenv import load_dotenv

load_dotenv()

BOT_NAME = 'book_scraper'

SPIDER_MODULES = ['book_scraper.spiders']
NEWSPIDER_MODULE = 'book_scraper.spiders'

# Соблюдаем robots.txt
ROBOTSTXT_OBEY = True

# Настройки MongoDB из переменных окружения
MONGO_URI = getenv('MONGO_URI', 'mongodb://localhost:27017/')
MONGO_DATABASE = getenv('MONGO_DATABASE', 'items')
MONGO_COLLECTION = getenv('MONGO_DATABASE_COLLECTION', 'scraped_books')

# Configure item pipelines
ITEM_PIPELINES = {
    # 'book_scraper.pipelines.MongoDBPipeline': 300,  # Comment this line
}

# MongoDB settings
MONGODB_URI = 'mongodb://localhost:27017'
MONGODB_DATABASE = 'books_db'
MONGODB_COLLECTION = 'books'

# Настройки задержек между запросами
DOWNLOAD_DELAY = 1.0
CONCURRENT_REQUESTS = 16 
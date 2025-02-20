import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE'),
            mongo_collection=crawler.settings.get('MONGODB_COLLECTION')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Проверяем обязательные поля
        required_fields = ['title', 'publication_year', 'isbn', 'pages_cnt', 'source_url']
        for field in required_fields:
            if not adapter.get(field):
                raise DropItem(f"Missing required field {field}")
        
        # Сохраняем в MongoDB
        self.db[self.mongo_collection].insert_one(adapter.asdict())
        return item 
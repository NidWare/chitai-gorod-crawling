import pymongo
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
import logging

class MongoDBPipeline:
    def __init__(self, mongo_uri, mongo_db, mongo_collection):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_collection = mongo_collection
        self.client = None
        self.db = None

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGODB_URI'),
            mongo_db=crawler.settings.get('MONGODB_DATABASE'),
            mongo_collection=crawler.settings.get('MONGODB_COLLECTION')
        )

    def open_spider(self, spider):
        try:
            self.client = pymongo.MongoClient(self.mongo_uri)
            self.db = self.client[self.mongo_db]
            logging.info(f"Successfully connected to MongoDB at {self.mongo_uri}")
        except Exception as e:
            logging.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def close_spider(self, spider):
        if self.client:
            self.client.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # Print item for debugging
        logging.info(f"Processing item: {adapter.asdict()}")
        
        try:
            # Check required fields
            required_fields = ['title', 'publication_year', 'isbn', 'pages_cnt', 'source_url']
            missing_fields = [field for field in required_fields if not adapter.get(field)]
            
            if missing_fields:
                raise DropItem(f"Missing required fields: {missing_fields}")
            
            # Save to MongoDB
            self.db[self.mongo_collection].insert_one(adapter.asdict())
            logging.info(f"Successfully saved item with ISBN {adapter.get('isbn')} to MongoDB")
            
            return item
            
        except Exception as e:
            logging.error(f"Error processing item: {str(e)}")
            raise DropItem(f"Failed to process item: {str(e)}") 
    
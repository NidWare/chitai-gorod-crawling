from scrapy import Item, Field

class BookItem(Item):
    title = Field()
    author = Field()
    description = Field()
    price_amount = Field()
    price_currency = Field()
    rating_value = Field()
    rating_count = Field()
    publication_year = Field()
    isbn = Field()
    pages_cnt = Field()
    publisher = Field()
    book_cover = Field()
    source_url = Field() 
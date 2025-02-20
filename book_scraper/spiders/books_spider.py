import scrapy
from scrapy.spiders import SitemapSpider
from book_scraper.items import BookItem

class BooksSpider(SitemapSpider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    sitemap_urls = ['http://books.toscrape.com/sitemap.xml']
    
    def parse(self, response):
        book = BookItem()
        
        book['title'] = response.xpath('//h1/text()').get()
        book['author'] = response.xpath('//table[@class="table table-striped"]//tr[1]/td/text()').get()
        book['description'] = response.xpath('//div[@id="product_description"]/following-sibling::p/text()').get()
        
        price = response.xpath('//p[@class="price_color"]/text()').get()
        if price:
            book['price_amount'] = int(float(price.replace('£', '')) * 100)
            book['price_currency'] = 'GBP'
            
        book['publication_year'] = 2024  # Пример, нужно извлечь из данных
        book['isbn'] = response.xpath('//table[@class="table table-striped"]//tr[1]/td/text()').get()
        book['pages_cnt'] = int(response.xpath('//table[@class="table table-striped"]//tr[2]/td/text()').get())
        book['source_url'] = response.url
        
        yield book 
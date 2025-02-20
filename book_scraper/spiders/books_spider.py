import scrapy
from scrapy.spiders import SitemapSpider
from book_scraper.items import BookItem
import re
import json

class BooksSpider(SitemapSpider):
    name = 'books'
    allowed_domains = ['chitai-gorod.ru']
    # We'll use only product sitemaps since they contain book pages
    sitemap_urls = ['https://www.chitai-gorod.ru/sitemap.xml']
    sitemap_rules = [
        ('/product/', 'parse_book'),  # Only process URLs containing /product/
    ]
    
    def sitemap_filter(self, entries):
        # Filter to include only product sitemaps
        for entry in entries:
            if 'products' in entry['loc']:
                yield entry

    def parse_book(self, response):
        book = BookItem()
        
        # Extract basic book information using JSON-LD data if available
        json_ld = response.xpath('//script[@type="application/ld+json"]/text()').get()
        if json_ld:
            try:
                data = json.loads(json_ld)
                if isinstance(data, list):
                    data = data[0]
                book['title'] = data.get('name')
                book['author'] = data.get('author', {}).get('name')
                book['isbn'] = data.get('isbn')
            except json.JSONDecodeError:
                pass

        # Fallback to xpath if JSON-LD is not available
        if not book.get('title'):
            book['title'] = response.css('h1::text').get()
        
        if not book.get('author'):
            # Extract author from the page
            book['author'] = response.css('.product-detail-page__author-value::text').get()
            
        # Extract price
        price_text = response.css('.product-price__value::text').get()
        if price_text:
            # Remove non-digit characters and convert to kopeks
            price = re.sub(r'[^\d.]', '', price_text)
            try:
                book['price_amount'] = int(float(price) * 100)
                book['price_currency'] = 'RUB'
            except ValueError:
                pass

        # Extract other details
        details = response.css('.product-detail-page__characteristics-item')
        for detail in details:
            label = detail.css('.product-detail-page__characteristics-label::text').get('')
            value = detail.css('.product-detail-page__characteristics-value::text').get('')
            
            if 'ISBN' in label:
                book['isbn'] = value.strip()
            elif 'страниц' in label.lower():
                try:
                    book['pages_cnt'] = int(re.sub(r'\D', '', value))
                except ValueError:
                    pass
            elif 'год' in label.lower():
                try:
                    book['publication_year'] = int(re.sub(r'\D', '', value))
                except ValueError:
                    pass

        book['description'] = response.css('.product-detail-page__description-text::text').get()
        book['source_url'] = response.url

        yield book 
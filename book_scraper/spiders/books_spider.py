import scrapy
from book_scraper.items import BookItem
import re
import logging
from scrapy_splash import SplashRequest

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['chitai-gorod.ru', 'localhost']  # Add localhost for Splash
    start_urls = ['https://www.chitai-gorod.ru/catalog/books-18030']
    
    custom_settings = {
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,
        'RANDOMIZE_DOWNLOAD_DELAY': True,
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Encoding': 'gzip, deflate, br',
        },
        'CONCURRENT_REQUESTS': 1,
        'SPLASH_URL': 'http://localhost:8050',
        'DUPEFILTER_CLASS': 'scrapy_splash.SplashAwareDupeFilter',
        'HTTPCACHE_STORAGE': 'scrapy_splash.SplashAwareFSCacheStorage',
    }

    def start_requests(self):
        lua_script = """
        function main(splash, args)
            splash:on_request(function(request)
                request:set_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
            end)
            assert(splash:go(args.url))
            splash:wait(2)
            return splash:html()
        end
        """
        
        for url in self.start_urls:
            yield SplashRequest(
                url,
                self.parse,
                endpoint='execute',
                args={
                    'lua_source': lua_script,
                    'wait': 2,
                },
                dont_filter=True
            )

    def parse(self, response):
        # Debug the response
        self.logger.info("Parsing main page")
        
        # Try different selectors for book links
        book_links = response.css('a[href*="/product/"]::attr(href)').getall()
        if not book_links:
            book_links = response.css('div.product-card a::attr(href)').getall()
        if not book_links:
            book_links = response.xpath('//a[contains(@href, "/product/")]/@href').getall()
            
        self.logger.info(f"Found {len(book_links)} book links")
        
        for link in book_links:
            absolute_url = response.urljoin(link)
            self.logger.info(f"Following book link: {absolute_url}")
            yield SplashRequest(
                absolute_url,
                self.parse_book,
                args={
                    'wait': 2,
                    'timeout': 90,
                }
            )

        # Follow pagination
        current_page = response.css('li.pagination__item--current::text').get()
        if current_page:
            next_page_num = int(current_page) + 1
            next_page_url = f'https://www.chitai-gorod.ru/catalog/books-18030?page={next_page_num}'
            self.logger.info(f"Following next page: {next_page_url}")
            yield SplashRequest(
                next_page_url,
                self.parse,
                args={
                    'wait': 2,
                    'timeout': 90,
                }
            )

    def parse_book(self, response):
        self.logger.info(f"Parsing book page: {response.url}")
        book = BookItem()
        
        try:
            # Extract title
            book['title'] = response.css('h1.detail-product__header-title::text').get('').strip()
            self.logger.info(f"Found title: {book['title']}")
            
            # Extract details from product-detail-features
            features = response.css('.product-detail-features__item')
            for feature in features:
                label = feature.css('.product-detail-features__item-title::text').get('').strip()
                value = feature.css('.product-detail-features__item-value::text').get('').strip()
                
                if not value:
                    value = feature.css('.product-detail-features__item-value--link::text').get('').strip()
                
                if 'ISBN' in label:
                    book['isbn'] = value
                elif 'Год издания' in label:
                    try:
                        book['publication_year'] = int(value)
                    except ValueError:
                        self.logger.warning(f"Failed to parse publication year: {value}")
                elif 'Издательство' in label:
                    book['publisher'] = value

            # Extract description
            description = response.css('.product-description-short__text::text').get('')
            if description:
                book['description'] = description.strip()

            # Extract price
            price_text = response.css('.product-price__value::text').get()
            if price_text:
                price = re.sub(r'[^\d.]', '', price_text)
                try:
                    book['price_amount'] = int(float(price) * 100)
                    book['price_currency'] = 'RUB'
                except ValueError:
                    self.logger.warning(f"Failed to parse price: {price_text}")

            # Extract author
            author = response.css('.product-detail-page__author-value::text').get('')
            if author:
                book['author'] = author.strip()

            # Extract book cover image URL
            book['book_cover'] = response.css('.product-info-gallery__poster::attr(src)').get()

            # Extract page count
            pages = response.xpath('//span[contains(text(), "Количество страниц")]/following-sibling::span/text()').get()
            if pages:
                try:
                    book['pages_cnt'] = int(re.sub(r'\D', '', pages))
                except ValueError:
                    self.logger.warning(f"Failed to parse page count: {pages}")

            book['source_url'] = response.url

            # Log the extracted data
            self.logger.info(f"Extracted book data: {book}")
            
            yield book

        except Exception as e:
            self.logger.error(f"Error parsing book page {response.url}: {str(e)}") 
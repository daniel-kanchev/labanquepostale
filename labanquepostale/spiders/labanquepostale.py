import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from labanquepostale.items import Article


class LabanquepostaleSpider(scrapy.Spider):
    name = 'labanquepostale'
    start_urls = ['https://www.labanquepostale.fr/particulier/mbp/actus.html']

    def parse(self, response):
        links = response.xpath('//article[@class="col-xs-12 js-has-link u-spacing-s-bottom"]/a/@href').getall()
        yield from response.follow_all(links, self.parse_article)

        next_page = response.xpath('(//a[@class="m-pagination__link m-pagination__link--next"])[1]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//time/text()').get()
        if date:
            date = date.strip()

        content = response.xpath('//main//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()

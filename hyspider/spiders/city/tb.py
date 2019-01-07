from hyspider.items.city import CityTB
from hyspider.spiders.browser import BrowserSpider


class CityTBSpider(BrowserSpider):
    name = 'city_tb'
    allowed_domains = ['taobao.com']
    start_urls = ['http://dianying.taobao.com']

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'hyspider.middlewares.city_tb.CityTBMiddleware': 543}
    }

    def parse(self, response):
        groups = response.css('.M-cityList li')
        for group in groups:
            g = group.css('label::text').extract()[0]
            cities = group.css('a')
            for city in cities:
                c = CityTB()
                c['id'] = city.css('::attr(data-id)').extract()[0]
                c['g'] = g
                c['name'] = city.css('::text').extract()[0]
                yield c

import json

import scrapy

from hyspider.items.city import CityLM


class CityLMSpider(scrapy.Spider):
    name = 'city_lm'
    allowed_domains = ['baidu.com']
    start_urls = ['http://dianying.baidu.com/common/city/citylist?hasLetter=false&isjson=true']

    # lm会对scray agent返回301 redirect
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'hyspider.middlewares.useragent.chrome.ChromeMiddleware': 543,
        }
    }

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        for city in res['data']['all']:
            c = CityLM()
            c['id'] = city['id']
            c['g'] = city['pinyin'][0].upper()
            c['name'] = city['name']
            yield c

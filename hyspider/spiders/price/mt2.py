import json

import scrapy
from hyspider.items.cinema import CinemaMT
from hyspider.items.city import CityMT
from hyspider.items.notification import NotificationMT
from hyspider.items.price import PriceMT
from hyspider.manager.cinema import CinemaManager
from hyspider.utils.log import logger


class MovieMT2Spider(scrapy.Spider):
    name = 'price_mt2'
    allowed_domains = ['maoyan.com']
    city = '上海'
    cinema_url = 'http://maoyan.com/cinema/{}'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'hyspider.middlewares.ipproxy.ProxyMiddleware': 100,
            'hyspider.middlewares.price.mt2.MT2PriceMiddleware': 200,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'hyspider.middlewares.useragent.random.UserAgentRandomMiddleware': 400
        }
    }

    def __init__(self, **kwargs):
        self.city_id = kwargs.get('city_id')
        self.city_name = CityMT.get_city_name(self.city_id)
        logger.info("city id %s, city name %s", self.city_id, self.city_name)

    def start_requests(self):
        cinema_manager = CinemaManager.get_instance()
        cinema_ids = cinema_manager.need_update_cinema_ids(CinemaMT, self.city_name)
        logger.info("There are %d cinemas to update", len(cinema_ids))
        # cinema_ids = [16409]
        for cinema_id in cinema_ids:
            yield scrapy.Request(self.cinema_url.format(cinema_id), meta={'cinema_id': cinema_id}, callback=self.parse)

    def parse(self, response):
        cinema_id = response.meta['cinema_id']
        schedules = json.loads(response.body_as_unicode())
        for schedule in schedules:
            p = PriceMT()
            p['cinema_id'] = schedule['cinema_id']
            p['movie_id'] = schedule['movie_id']
            p['show_date'] = schedule['show_date']
            p['begin'] = schedule['begin']
            p['end'] = schedule['end']
            p['language'] = schedule['language']
            p['hall'] = schedule['hall']
            p['price'] = schedule['price']
            yield p

        n = NotificationMT()
        n['cinema_id'] = cinema_id
        yield n
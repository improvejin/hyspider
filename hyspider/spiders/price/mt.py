import json
import random

import scrapy
from hyspider.items.cinema import CinemaMT
from hyspider.items.notification import NotificationMT
from hyspider.items.price import PriceMT
from hyspider.manager.cinema import CinemaManager
from hyspider.spiders.browser import BrowserSpider
from hyspider.utils.useragents import mb_user_agents


class MovieMTSpider(BrowserSpider):
    name = 'price_mt'
    allowed_domains = ['m.maoyan.com']
    city = '上海'

    cinema_url = 'http://m.maoyan.com/shows/{}'

    url = 'http://m.maoyan.com/ajax/cinemaDetail?cinemaId={}'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'hyspider.middlewares.price.mt.MTPriceMiddleware': 543
        }
    }

    def custom_browser_options(self):
        self.chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36"')
        #self.chrome_options.add_argument('user-agent="{}"'.format(random.choice(mb_user_agents)))

    def start_requests(self):
        cinema_manager = CinemaManager.get_instance()
        cinema_ids = cinema_manager.need_update_cinema_ids(CinemaMT)
        cinema_ids = [6, 12]
        for cinema_id in cinema_ids:
            yield scrapy.Request(self.cinema_url.format(cinema_id), meta={'cinema_id': cinema_id}, callback=self.parse)

    def parse(self, response):
        cinema_id = response.meta['cinema_id']
        movies = json.loads(response.body_as_unicode())
        for movie in movies:
            for show in movie['shows']:
                p = PriceMT()
                p['cinema_id'] = cinema_id
                p['movie_id'] = int(movie['movieId'])
                p['show_date'] = show['show_date']
                p['begin'] = show['begin']
                p['end'] = show['end']
                p['language'] = show['language']
                p['hall'] = show['hall']
                p['price'] = float(show['price'])
                yield p

        n = NotificationMT()
        n['cinema_id'] = int(cinema_id)
        yield n
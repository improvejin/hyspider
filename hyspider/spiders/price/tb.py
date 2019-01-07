import json

import scrapy

from hyspider.items.cinema import CinemaTB
from hyspider.items.notification import NotificationTB
from hyspider.items.price import PriceTB
from hyspider.manager.cinema import CinemaManager
from hyspider.spiders.browser import BrowserSpider


class MovieSpider(BrowserSpider):
    name = 'price_tb'
    allowed_domains = ['h5.m.taopiaopiao.com']
    city = '上海'
    cinema_url = 'https://h5.m.taopiaopiao.com/app/moviemain/pages/show-list/index.html?cinemaid={}'
    mobile_emulation = {'deviceName': 'iPhone X'}
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'hyspider.middlewares.price.tb.TBPriceMiddleware': 543}
    }

    def custom_browser_options(self):
        self.chrome_options.add_experimental_option('mobileEmulation', self.mobile_emulation)
        self.chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36"')

    def start_requests(self):
        cinema_manager = CinemaManager.get_instance()
        # cinema_ids = cinema_manager.load_cinema_ids(CinemaTB)
        cinema_ids = cinema_manager.need_update_cinema_ids(CinemaTB)
        # cinema_ids = [4664]
        for cinema_id in cinema_ids:
            yield scrapy.Request(self.cinema_url.format(cinema_id), meta={'cinema_id': cinema_id}, callback=self.parse)

    def parse(self, response):
        cinema_id = response.meta['cinema_id']
        movies = json.loads(response.body_as_unicode())
        for movie in movies:
            for show in movie['shows']:
                p = PriceTB()
                p['cinema_id'] = cinema_id
                p['movie_id'] = int(movie['movie_id'])
                p['show_date'] = show['show_date']
                p['begin'] = show['begin']
                p['end'] = show['end']
                p['language'] = show['language']
                p['hall'] = show['hall']
                p['price'] = float(show['price'])
                yield p

        n = NotificationTB()
        n['cinema_id'] = int(cinema_id)
        yield n
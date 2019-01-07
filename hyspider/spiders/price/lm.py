import re
from datetime import date

import scrapy

from hyspider.items.cinema import CinemaLM
from hyspider.items.city import CityLM
from hyspider.items.notification import NotificationLM
from hyspider.items.price import PriceLM
from hyspider.manager.cinema import CinemaManager
from hyspider.utils.log import logger


class MovieLMSpider(scrapy.Spider):
    name = 'price_lm'
    allowed_domains = ['baidu.com']
    url = 'https://mdianying.baidu.com/cinema/detail?cinemaId={}&from=webapp&sub_channel=wise_shoubai_movieScheduleWeb&c={}'

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 10,  # 移动端响应可能比较慢
        'DOWNLOADER_MIDDLEWARES': {
            'hyspider.middlewares.ipproxy.ProxyMiddleware': 100,
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'hyspider.middlewares.useragent.random.UserAgentRandomMiddleware': 400
        }
    }

    def __init__(self, **kwargs):
        self.city_id = kwargs.get('city_id')
        self.city_name = CityLM.get_city_name(self.city_id)
        logger.info("city id %s, city name %s", self.city_id, self.city_name)

    # lm h5 web差别大
    def start_requests(self):
        cinema_manager = CinemaManager.get_instance()
        cinema_ids = cinema_manager.need_update_cinema_ids(CinemaLM, self.city_name)
        # cinema_ids = [11277]
        logger.info("There are %d cinemas to update", len(cinema_ids))
        for cinema_id in cinema_ids:
            # time.sleep(random.randint(1, 10))
            yield scrapy.Request(self.url.format(cinema_id, self.city_id), callback=self.parse)

    def parse(self, response):
        cinema_head_node = response.css('.cinema-head')
        cinema_id = re.search('cinemaId=([\d]*)', cinema_head_node.css('::attr(href)').extract()[0]).group(1)

        movie_ids = list()
        movie_ids_node = response.css('.m-movies').css('.movies li')
        for movie_id_node in movie_ids_node:
            movie_id = movie_id_node.css('::attr(data-movie-id)').extract()[0]
            movie_ids.append(movie_id)
        for movie_id in movie_ids:
            schedule_class = '.movie-{}'.format(movie_id)
            schedules_node = response.css(schedule_class).css('.daily-schedule')
            for schedule_node in schedules_node:
                p = PriceLM()
                p['cinema_id'] = int(cinema_id)
                p['movie_id'] = int(movie_id)
                p['show_date'] = date.fromtimestamp(int(schedule_node.css('::attr(data-date)').extract()[0]) / 1000).isoformat()
                p['begin'] = schedule_node.css('.start::text').extract()[0]
                p['end'] = schedule_node.css('.end::text').extract()[0].rstrip('散场')
                p['language'] = schedule_node.css('.lan::text').extract()[0]
                p['hall'] = schedule_node.css('.theater::text').extract()[0]
                p['price'] = float(schedule_node.css('.price-info .price').css('::text')[2].extract())
                yield p

        n = NotificationLM()
        n['cinema_id'] = int(cinema_id)
        yield n

import json
import re

import scrapy
from hyspider.items.cinema import CinemaTB
from hyspider.items.city import CityTB
from hyspider.items.notification import NotificationTB
from hyspider.items.price import PriceTB
from hyspider.manager.cinema import CinemaManager
from hyspider.utils.log import logger
from hyspider.utils.proxy import get_random_ip_port


class MovieTB2Spider(scrapy.Spider):
    name = 'price_tb2'
    allowed_domains = ['taopiaopiao.com']
    city = '上海'

    cinema_url = 'https://www.taopiaopiao.com/cinemaDetail.htm?cinemaId={}'
    cinema_schedule ='https://www.taopiaopiao.com/cinemaDetailSchedule.htm?{}'

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'hyspider.middlewares.price.tb2.TB2PriceMiddleware': 200,
        },
        # 'COOKIES_ENABLED': True,
        'RETRY_ENABLED': False
    }

    def __init__(self, **kwargs):
        self.city_id = kwargs.get('city_id')
        self.city_name = CityTB.get_city_name(self.city_id)
        logger.info("city id %s, city name %s", self.city_id, self.city_name)

    def start_requests(self):
        cinema_manager = CinemaManager.get_instance()
        cinema_ids = cinema_manager.need_update_cinema_ids(CinemaTB, self.city_name)
        logger.info("There are %d cinemas to update", len(cinema_ids))
        # cinema_ids = [37000]
        for cinema_id in cinema_ids:
            # special usage
            proxy = get_random_ip_port()
            # proxy = None
            yield scrapy.Request(self.cinema_url.format(cinema_id), callback=self.parse, meta={'cinema_id': cinema_id, 'proxy': proxy})

    def parse(self, response):
        cinema_id = response.meta['cinema_id']

        schedules = json.loads(response.body_as_unicode())
        # schedules.append(n)
        for schedule in schedules:
            # if isinstance(schedule, NotificationTB):
            #     p = schedule
            # else:
            p = PriceTB()
            p['cinema_id'] = schedule['cinema_id']
            p['movie_id'] = schedule['movie_id']
            p['show_date'] = schedule['show_date']
            p['begin'] = schedule['begin']
            p['end'] = schedule['end']
            p['language'] = schedule['language']
            p['hall'] = schedule['hall']
            p['price'] = schedule['price']
            yield p
        n = NotificationTB()
        n['cinema_id'] = int(cinema_id)
        yield n

    def parse_cinema(self, response):
        ajax_req = response.css('.schedule-wrap::attr(data-param)').extract()[0]
        yield scrapy.Request(self.cinema_schedule.format(ajax_req), callback=self.parse_movies, cookies=response.request.cookies, meta=response.meta)

    def parse_movies(self, response):
        tags = response.css('.select-tags')
        if len(tags) > 0:
            links = tags[0].css('a::attr(data-param)').extract()
            for link in links:
                yield scrapy.Request(self.cinema_schedule.format(link), callback=self.parse_show_dates, cookies=response.request.cookies, meta=response.meta)
        else:
            n = NotificationTB()
            n['cinema_id'] = int(response.meta['cinema_id'])
            yield n

    def parse_show_dates(self, response):
        tags = response.css('.select-tags')
        if len(tags) > 1:
            links = tags[1].css('a::attr(data-param)').extract()
            for link in links:
                yield scrapy.Request(self.cinema_schedule.format(link), callback=self.parse_schedules, cookies=response.request.cookies, meta=response.meta)

    def parse_schedules(self, response):
        groups = re.search('cinemaId=([\d]*)&activityId=&fCode=&showId=([\d]*)&showDate=([\S]*)&ts', response.url)
        cinema_id = groups.group(1)
        movie_id = groups.group(2)
        show_date = groups.group(3)
        shows = response.css('tbody tr')
        for show in shows:
            p = PriceTB()
            p['cinema_id'] = cinema_id
            p['movie_id'] = movie_id
            p['show_date'] = show_date
            p['begin'] = show.css('.hall-time em').css('::text').extract()[0]
            p['end'] = show.css('.hall-time').css('::text').extract()[2].strip().lstrip('预计').lstrip('次日').rstrip('散场')
            p['language'] = show.css('.hall-type::text').extract()[0].strip()
            p['hall'] = show.css('.hall-name::text').extract()[0].strip()
            p['price'] = show.css('.now::text').extract()[0]
            yield p

        n = NotificationTB()
        n['cinema_id'] = int(cinema_id)
        yield n
# -*- coding: utf-8 -*-
import scrapy
import json
from urllib.request import urlopen
from bs4 import BeautifulSoup

from hyspider import settings
from hyspider.items.cinema import CinemaMT
from hyspider.items.city import CityMT
from hyspider.utils.geo_util import get_district, parse_addr, get_district_from_lat_lng


class CinemaMTSpider(scrapy.Spider):
    name = 'cinema_mt'
    allowed_domains = ['maoyan.com']
    start_url = 'http://m.maoyan.com/ajax/cinemaList?offset=0&limit=500&districtId=-1&cityId={}'

    def __init__(self, city_id, **kwargs):
        self.city_id = city_id
        self.city_name = CityMT.get_city_name(city_id)

    def start_requests(self):
        yield scrapy.Request(self.start_url.format(self.city_id), callback=self.parse)

    def parse(self, response):
        res = json.loads(response.body_as_unicode())
        cinemas = res['cinemas']
        c = CinemaMT()
        c['city'] = self.city_name
        for cinema in cinemas:
            c['id'] = cinema['id']
            if len(cinema['sellPrice']) > 0:
                c['min_price'] = float(cinema['sellPrice'])

            if not settings.UPDATE_MIN_PRICE:
                c['name'] = cinema['nm'].upper()
                c['addr'] = cinema['addr'].strip()
                c['district'] = get_district(c['addr'])
                try:
                    c['phone'] = CinemaMTSpider.get_phone(c['id'])
                except:
                    c['phone'] = ''
                lat_lng = parse_addr(c['city'], c['addr'])
                if lat_lng is not None:
                    c['lat_lng'] = lat_lng['lat_lng']
                    c['location'] = lat_lng['location']
                    c['precise'] = lat_lng['precise']
                    c['confidence'] = lat_lng['confidence']
                    if len(c['district']) == 0:
                        c['district'] = get_district_from_lat_lng(c['lat_lng'])
            yield c

    @classmethod
    def get_phone(cls, id):
        url = 'http://maoyan.com/cinema/{}'.format(id)
        html = urlopen(url)
        bs = BeautifulSoup(html)
        phone = bs.select('.telphone')[0].get_text()
        index = phone.find('：')
        if index != -1:
            return phone[index+1:].strip()
        else:
            return phone.strip()

    # def parse1(self, response):
    #     city = response.css('.city-container')
    #     current_city_id = city.css('::attr(data-val)').extract()[0].split(':')[1].strip(' }')
    #     city_name = city.css('.city-name').css('::text').extract()[0].strip('\n').strip()
    #
    #     brands = response.css('li[data-type="brand"]').css('a')
    #     cinema_brand = CinemaBrand()
    #     for brand in brands:
    #         cinema_brand['name'] = brand.css('::text').extract()[0]
    #         cinema_brand['url'] = brand.css('::attr(href)').extract()[0]
    #         cinema_brand['id'] = brand.css('::attr(data-id)').extract()[0]
    #         yield cinema_brand
    #
    #     districts = response.css('li[data-type="district"]').css('a')
    #     district = District()
    #     district['city_name'] = city_name
    #     district['city_id'] = current_city_id
    #     for d in districts:
    #         district['name'] = d.css('::text').extract()[0]
    #         district['url'] = d.css('::attr(href)').extract()[0]
    #         district['id'] = d.css('::attr(data-id)').extract()[0]
    #         yield district
    #
    #     hall_types = response.css('li[data-type="hallType"]').css('a')
    #     hall = Hall()
    #     for h in hall_types:
    #         hall['name'] = h.css('::text').extract()[0]
    #         hall['url'] = h.css('::attr(href)').extract()[0]
    #         hall['id'] = h.css('::attr(data-id)').extract()[0]
    #         yield hall
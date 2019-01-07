import json
import re
from urllib.request import urlopen

import scrapy
from bs4 import BeautifulSoup
from scrapy.http import TextResponse

from hyspider import settings
from hyspider.items.cinema import CinemaLM
from hyspider.items.city import CityLM
from hyspider.utils.geo_util import get_district, parse_addr, get_district_from_lat_lng


class CinemaLMSpider(scrapy.Spider):
    name = 'cinema_lm'
    allowed_domains = ['taobao.com']
    start_urls_lm = 'https://mdianying.baidu.com/movie/cinema?sfrom=wise_shoubai&c={}&cc=&lat=&lng=&MOVIETOKEN=944244989d386f8ffbf98db708353f28&device=2_404_&pn={}&isAppend=1'
    phone_url = 'https://mdianying.baidu.com/cinema/info?cinemaId='

    channel = 'lm'
    count = 0

    custom_settings = {
        'DOWNLOAD_TIMEOUT': 15,  #移动端响应可能比较慢
        'DOWNLOADER_MIDDLEWARES': {
            'hyspider.middlewares.useragent.chrome.ChromeMiddleware': 543
        }
    }

    def __init__(self, city_id, **kwargs):
        self.city_id = city_id
        self.city_name = CityLM.get_city_name(city_id)

    def start_requests(self):
        for i in range(0, 31):
            yield scrapy.Request(self.start_urls_lm.format(self.city_id, i), callback=self.parse)

    def parse(self, response):

        res = json.loads(response.body_as_unicode())
        html = res['data']['html']

        response = TextResponse(url=response.urljoin(''), body=html, encoding='utf-8')
        if len(response.body_as_unicode()) == 0:
            return

        cinemas = response.css('.portal-cinema-list-item')
        c = CinemaLM()
        c['city'] = self.city_name
        for cinema in cinemas:
            self.count = self.count+1
            id_href = cinema.css('a')
            c['id'] = re.search('cinemaId=([\d]+)', id_href.css('::attr(href)').extract()[0]).group(1)
            if c['id']=='8131':
                print("hi")
            price_node = cinema.css('.portal-cinema-price-num')
            if len(price_node) > 0:
                c['min_price'] = price_node.css('::text').extract()[0]

            if not settings.UPDATE_MIN_PRICE:
                c['name'] = cinema.css('.portal-cinema-name').css('::text').extract()[0].upper().replace('（', '(').replace('）', ')')
                c['addr'] = cinema.css('.portal-cinema-address-section').css('::text').extract()[0].replace('（', '(').replace('）', ')')
                c['phone'] = self.get_phone(c['id'])
                c['district'] = get_district(c['addr'], c['city'])
                lat_lng = parse_addr(c['city'], c['addr'])
                if lat_lng is not None:
                    c['lat_lng'] = lat_lng['lat_lng']
                    c['location'] = lat_lng['location']
                    c['precise'] = lat_lng['precise']
                    c['confidence'] = lat_lng['confidence']
                    if len(c['district']) == 0 or len(c['district']) > 6:
                        c['district'] = get_district_from_lat_lng(c['lat_lng'])
            yield c

        print("total:",  self.count)

    def get_phone(self, id):
        url = self.phone_url+id
        html = urlopen(url)
        bs = BeautifulSoup(html)
        phone = ''
        phone_node = bs.select('.phones-list > a')
        if len(phone_node) > 0:
            phone = phone_node[0].get_text()
        return phone

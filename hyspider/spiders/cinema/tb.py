import re
import scrapy

from hyspider import settings
from hyspider.items.cinema import CinemaTB
from hyspider.items.city import CityTB
from hyspider.utils.geo_util import get_district, parse_addr, get_district_from_lat_lng


class CinemaTBSpider(scrapy.Spider):
    name = 'cinema_tb'
    allowed_domains = ['taobao.com']
    start_urls_tb = 'https://dianying.taobao.com/ajaxCinemaList.htm?page={}&regionName=&cinemaName=&pageSize=30&pageLength=28&sortType=0&n_s=new&city={}'

    def __init__(self, city_id, **kwargs):
        self.city_id = city_id
        self.city_name = CityTB.get_city_name(city_id)

    def start_requests(self):
        if settings.UPDATE_MIN_PRICE:
            yield scrapy.Request(self.price_url_tb, callback=self.parse_price)
        else:
            for i in range(1, 11):
                yield scrapy.Request(self.start_urls_tb.format(i, self.city_id), callback=self.parse)

    def parse(self, response):
        if len(response.body_as_unicode()) == 0:
            return

        details = response.css('.detail-middle')
        c = CinemaTB()
        c['city'] = self.city_name
        for detail in details:
            cinema = detail.css('h4 a')
            c['id'] = re.search('cinemaId=(.*)&', cinema.css('::attr(href)').extract()[0]).group(1)
            c['name'] = cinema.css('::text').extract()[0].upper().replace('（', '(').replace('）', ')')
            c['addr'] = detail.css('.limit-address').css('::text').extract()[0].replace('（', '(').replace('）', ')')
            c['district'] = get_district(c['addr'])
            c['phone'] = detail.css('.middle-p-list')[1].css('::text').extract()[1].replace(',', '-')
            # 通过web无法获取cinema最低价
            # c['price'] = self.parse_price(c['id'])
            lat_lng = parse_addr(c['city'], c['addr'])
            if lat_lng is not None:
                c['lat_lng'] = lat_lng['lat_lng']
                c['location'] = lat_lng['location']
                c['precise'] = lat_lng['precise']
                c['confidence'] = lat_lng['confidence']
                if len(c['district']) == 0:
                    c['district'] = get_district_from_lat_lng(c['lat_lng'])
            yield c

    def parse_price(self, response):
        pass

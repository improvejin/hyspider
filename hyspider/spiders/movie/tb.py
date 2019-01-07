import re
import scrapy

from hyspider.items.movie import MovieTB


class MovieTBSpider(scrapy.Spider):
    name = 'movie_tb'
    allowed_domains = ['dianying.taobao.com']
    start_urls = ['https://dianying.taobao.com/showList.htm?city=310100']
    city = '上海'
    channel = 'tb'

    def parse(self, response):
        tab_content = response.css('.tab-content')[0]
        showing = tab_content.xpath('./div[1]')
        coming = tab_content.xpath('./div[2]')
        return self.parse_movie(showing, coming)

    # 生成器如何合并
    def parse_movie(self, showing, coming):
        cards = showing.css('.movie-card')
        # 少部分电影同时在showing和coming
        for card in cards:
            m = MovieTB()
            m['id'] = int(re.search('showId=(\d+)', card.css('::attr(href)').extract()[0]).group(1))
            m['name'] = card.css('.movie-card-name .bt-l').css('::text').extract()[0]
            score = card.css('.movie-card-name .bt-r').css('::text').extract()
            m['score'] = score[0] if len(score) > 0 else 0
            m['poster'] = card.xpath('./div[2]/img/@src').extract()[0]
            card_info = card.css('.movie-card-list')
            m['actors'] = card_info.xpath('./span[2]/text()').extract()[0][3:]
            m['ongoing'] = 1
            yield m

        cards = coming.css('.movie-card')
        for card in cards:
            m = MovieTB()
            m['id'] = int(re.search('showId=(\d+)', card.css('::attr(href)').extract()[0]).group(1))
            m['name'] = card.css('.movie-card-name .bt-l').css('::text').extract()[0]
            score = card.css('.movie-card-name .bt-r').css('::text').extract()
            m['score'] = score[0] if len(score) > 0 else 0
            m['poster'] = card.xpath('./div[2]/img/@src').extract()[0]
            card_info = card.css('.movie-card-list')
            m['actors'] = card_info.xpath('./span[2]/text()').extract()[0][3:]
            m['ongoing'] = 0
            yield m

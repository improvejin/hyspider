import json

import scrapy

from hyspider.items.movie import MovieMT


class MovieMTSpider(scrapy.Spider):
    name = 'movie_mt'
    allowed_domains = ['m.maoyan.com']
    start_urls = ['http://m.maoyan.com/ajax/movieOnInfoList?token=', 'http://m.maoyan.com/ajax/comingList?ci=10&token=&limit=10']
    coming_url = 'http://m.maoyan.com/ajax/moreComingList?token=&movieIds='

    def parse(self, response):
        body = json.loads(response.body_as_unicode())
        ids = body['movieIds']
        total = len(ids)
        ids_str = [str(id) for id in ids]
        page = divmod(total, 10)[0]
        if 'total' in body:
            callback = self.parse_ongoing
        else:
            callback = self.parse_coming
        for i in range(page):
            start = i*10
            end = start+10
            url = self.coming_url + ','.join(ids_str[start:end])
            #print(url)
            yield scrapy.Request(url, callback)

        url = self.coming_url + ','.join(ids_str[end:total])
        yield scrapy.Request(url, callback)

    # 回调函数需返回一个生成器
    def parse_ongoing(self, response):
        return self.parse_movie(response, 1)

    def parse_coming(self, response):
        return self.parse_movie(response, 0)

    def parse_movie(self, response, ongoing):
        body = json.loads(response.body_as_unicode())
        movies = body['coming']
        for movie in movies:
            m = MovieMT()
            m['id'] = movie['id']
            m['name'] = movie['nm']
            m['score'] = float(movie['sc'])
            m['poster'] = movie['img']
            m['version'] = movie['version']
            m['release_date'] = movie['rt']
            m['actors'] = movie.get('star', '')
            m['ongoing'] = ongoing
            yield m


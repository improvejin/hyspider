import json

import requests
import scrapy

from hyspider.items.movie import MovieDB
from hyspider.utils.log import logger


class MovieDBSpider(scrapy.Spider):
    name = 'movie_db'
    allowed_domains = ['douban.com']
    in_theaters = 'https://api.douban.com/v2/movie/in_theaters?count=100'
    coming_soon = 'https://api.douban.com/v2/movie/coming_soon?count=200'

    city = '上海'
    channel = 'db'

    # db会对scray agent返回403
    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'hyspider.middlewares.useragent.chrome.ChromeMiddleware': 543,
        }
    }

    def start_requests(self):
        yield scrapy.Request(self.in_theaters, meta={'ongoing': 1}, callback=self.parse)
        yield scrapy.Request(self.coming_soon, meta={'ongoing': 0}, callback=self.parse)

    def parse(self, response):
        ongoing = response.meta['ongoing']
        body = json.loads(response.body_as_unicode())
        for movie in body['subjects']:
            m = MovieDB()
            m['id'] = movie['id']
            m['name'] = movie['title']
            m['type'] = '|'.join(movie['genres'])
            m['score'] = movie['rating']['average']
            m['poster'] = movie['images']['large']
            m['actors'] = ','.join([cast['name'] for cast in movie['casts']])
            m['release_date'] = movie['year']
            m['ongoing'] = ongoing
            duration = self.parse_duration(movie['id'])
            if duration is not None:
                m['duration'] = duration
            yield m

    def parse_duration(self, movie_id):
        try:
            r = requests.get('https://movie.douban.com/subject/{}/'.format(movie_id))
            from bs4 import BeautifulSoup
            bs = BeautifulSoup(r.text)
            node = bs.find(property="v:runtime")
            if node is not None:
                return node.get_text()
        except Exception as e:
            logger.exception('Error')
        return None

# if __name__ == '__main__':
#       parse_duration(26752088)

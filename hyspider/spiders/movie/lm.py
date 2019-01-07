import json
import scrapy
from scrapy.http import TextResponse
from hyspider.items.movie import MovieLM


class MovieLMSpider(scrapy.Spider):
    name = 'movie_lm'
    allowed_domains = ['baidu.com']
    currentPage = 0
    coming_url = 'https://mdianying.baidu.com/api/movie/upcoming?c=289MOVIETOKEN=944244989d386f8ffbf98db708353f28&device=2_404_&page=movie&pageNum={}'
    start_urls = ['https://mdianying.baidu.com/movie/movie?sfrom=wise_shoubai&c=289MOVIETOKEN=944244989d386f8ffbf98db708353f28&device=2_404_',
                  'https://mdianying.baidu.com/api/movie/upcoming?c=289MOVIETOKEN=944244989d386f8ffbf98db708353f28&device=2_404_&page=movie&pageNum=0']

    city = '上海'
    channel = 'lm'

    def start_requests(self):
        callbacks = [self.parse_ongoing, self.parse_coming]
        for i in range(len(self.start_urls)):
            yield scrapy.Request(self.start_urls[i], callback=callbacks[i])

    def parse_ongoing(self, response):
        res = json.loads(response.body_as_unicode())
        html = res['data']['html']

        response = TextResponse(url=response.urljoin(''), body=html, encoding='utf-8')
        if len(response.body_as_unicode()) == 0:
            return

        movies = response.css('.movie-list-item')

        for movie in movies:
            m = MovieLM()
            m['id'] = movie.css('.poster-show').css('::attr(data-movieid)').extract()[0]
            m['name'] = movie.css('.movie-name-text').css('::text').extract()[0]
            fen = movie.css('.fen')
            if len(fen) > 0:
                m['score'] = fen.css('::text').extract()[0]
            m['ongoing'] = 1
            yield m

    def parse_coming(self, response):
        res = json.loads(response.body_as_unicode())
        movies = res['list']
        for movie in movies:
            m = MovieLM()
            m['id'] = movie['movieId']
            m['name'] = movie['name']
            m['actors'] = movie['actors'].replace('、', ',').strip("'")
            m['poster'] = movie['imageSrc']
            m['release_date'] = movie['releaseDateDesc']
            m['ongoing'] = 0
            yield m

        self.currentPage += 1
        if res['hasNextPage']:
            yield scrapy.Request(self.coming_url.format(self.currentPage), callback=self.parse_coming)

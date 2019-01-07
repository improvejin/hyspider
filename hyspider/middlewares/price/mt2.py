import json

import re
from scrapy import signals
from scrapy.http import TextResponse

from hyspider.utils.font_util import MTFontParser


class MT2PriceMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        return None

    def process_response(self, request, response, spider):
        if response.status != 200:
            return None
        font_style = response.css('style::text').extract()[0]
        font_file = 'http:' + re.search("'([\S]*woff)'", font_style).group(1)
        font_parser = MTFontParser(font_file)
        res = list()
        shows = response.css('.show-list')
        for show in shows:
            plists = show.css('.plist-container')
            for i in range(0, len(plists)):
                schedules = plists[i].css('tbody').css('tr')
                for schedule in schedules:
                    d = dict()
                    d['begin'] = schedule.css('.begin-time::text').extract()[0]
                    d['end'] = schedule.css('.end-time::text').extract()[0].rstrip('散场')
                    d['language'] = schedule.css('.lang::text').extract()[0]
                    d['hall'] = schedule.css('.hall::text').extract()[0]
                    d['price'] = font_parser.parse_price(schedule.css('.stonefont::text').extract()[0])
                    meta = schedule.css('a').css('::attr(href)').extract()[0]
                    groups = re.search('/([\d]*)\?movieId=([\d]*)&cinemaId=([\d]*)', meta)
                    # s = groups.group(1)[0:8]
                    d['show_date'] = groups.group(1)[0:8]
                    d['movie_id'] = int(groups.group(2))
                    d['cinema_id'] = int(groups.group(3))
                    res.append(d)

        content = json.dumps(res)
        body = content.encode('utf-8')
        response = TextResponse(url=request.url, request=request, body=body)
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

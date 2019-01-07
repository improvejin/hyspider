import json
import re
import requests
from bs4 import BeautifulSoup
from scrapy import signals
from scrapy.http import TextResponse


class TB2PriceMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def get_cookies(self, cinema_id, proxies):
        # rsp = requests.get('https://www.taopiaopiao.com/cinemaDetail.htm?cinemaId={}'.format(cinema_id), allow_redirects=False)
        # login = rsp.headers.get('Location')
        login = 'https://login.taobao.com/jump?target=https://www.taopiaopiao.com/cinemaDetail.htm?cinemaId={}'.format(cinema_id)
        rsp = requests.get(login, allow_redirects=False)
        add_cookies = rsp.headers.get('Location')
        rsp = requests.get(add_cookies, allow_redirects=False, proxies=proxies)
        return rsp.cookies.get_dict()

    def process_request(self, request, spider):
        cinema_id = request.meta['cinema_id']
        proxies = {'http': request.meta['proxy']}
        cookies = self.get_cookies(cinema_id, proxies)
        rsp = requests.get('https://www.taopiaopiao.com/cinemaDetail.htm?cinemaId={}'.format(cinema_id),
                           allow_redirects=False, cookies=cookies, proxies=proxies)
        bs = BeautifulSoup(rsp.text)
        detail = bs.select_one('.schedule-wrap').attrs['data-param']
        rsp = requests.get('https://www.taopiaopiao.com/cinemaDetailSchedule.htm?' + detail, allow_redirects=False,
                           cookies=cookies, proxies=proxies)

        res = list()
        bs = BeautifulSoup(rsp.text)
        select_tags = bs.select_one('.select-tags')
        if select_tags is not None:
            movies = select_tags.select('a')
            for movie in movies:
                rsp = requests.get('https://www.taopiaopiao.com/cinemaDetailSchedule.htm?' + movie.attrs['data-param'],
                                   allow_redirects=False, cookies=cookies, proxies=proxies)
                bs = BeautifulSoup(rsp.text)
                dates = bs.select('.select-tags')[1].select('a')
                for date in dates:
                    param = date.attrs['data-param']
                    groups = re.search('showId=([\d]*)&showDate=([\S]*)&ts', param)
                    movie_id = groups.group(1)
                    show_date = groups.group(2)
                    rsp = requests.get('https://www.taopiaopiao.com/cinemaDetailSchedule.htm?' + param,
                                       allow_redirects=False, cookies=cookies, proxies=proxies)
                    bs = BeautifulSoup(rsp.text)
                    schedules = bs.select('tbody tr')
                    for schedule in schedules:
                        p = dict()
                        p['cinema_id'] = cinema_id
                        p['movie_id'] = movie_id
                        p['show_date'] = show_date
                        p['begin'] = schedule.select_one('.hall-time em').get_text()
                        x = re.search('[\d]*:[\d]*', schedule.select_one('.hall-time ').contents[-1])
                        if x is not None:
                            p['end'] = x.group(0)
                        else:
                            p['end'] = ''
                        p['language'] = schedule.select_one('.hall-type').get_text().strip()
                        p['hall'] = schedule.select_one('.hall-name').get_text().strip()
                        p['price'] = schedule.select_one('.now').get_text().strip()
                        res.append(p)

        content = json.dumps(res)
        body = content.encode('utf-8')
        response = TextResponse(url=request.url, request=request, body=body)
        return response

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


if __name__ == '__main__':
    from hyspider.utils.proxy import get_random_ip_port
    import scrapy
    req = scrapy.Request('https://www.taopiaopiao.com/cinemaDetail.htm?cinemaId=4290', meta={'cinema_id': 13771, 'proxy': get_random_ip_port()})
    m = TB2PriceMiddleware()
    rsp = m.process_request(req, None)
    print(rsp)
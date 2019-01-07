import json
import re

import time
from bs4 import BeautifulSoup

from hyspider.middlewares.browser import BrowserMiddleware
from hyspider.utils.font_util import MTFontParser


class MTPriceMiddleware(BrowserMiddleware):

    woff_pattern = re.compile('base64,(.*)\) format')

    def get_response_content(self, chrome):
        movie_shows = list()
        posters = chrome.find_elements_by_class_name('swiper-slide')
        # 获取woff需在获取post ajax后，ajax后的html中woff会变，所以顺序很关键
        stone_font = self.woff_pattern.search(chrome.page_source).group(1)
        parser = MTFontParser(stone_font)
        for poster in posters:
            poster.click()
            #time.sleep(1)  # 等待影片信息切换
            self.wait_active_by_class(chrome, poster, 'swiper-slide-active')
            self.wait_visible_by_class(chrome, 'nav-item')
            movie_info = self.parse_movie_info(chrome.page_source)
            dates = chrome.find_elements_by_class_name('nav-item')      # try except
            movie_info['shows'] = list()
            for date in dates:
                date.click()
                self.wait_active_by_class(chrome, date, 'active')
                movie_info['shows'].extend(self.parse_movie_shows(chrome.page_source, parser))
            movie_shows.append(movie_info)
            self.hidde_element_by_class(chrome, 'nav-item')
        return json.dumps(movie_shows)

    def parse_movie_info(self, html):
        bs = BeautifulSoup(html)
        active_movie = bs.select('.swiper-slide-active')[0]
        d = active_movie.attrs['data-obj']
        return json.loads(d)

    def parse_movie_shows(self, html, parser):
        bs = BeautifulSoup(html)
        shows = list()
        active_date = bs.select('.active')[0]
        date = active_date.attrs['data-id']
        seats = bs.select('.seat-list .item-outer')
        for seat in seats:
            show = dict()
            show['show_date'] = date
            show['begin'] = seat.select('.begin')[0].get_text()
            show['end'] = seat.select('.end')[0].get_text().rstrip('散场')
            show['language'] = seat.select('.lan')[0].get_text()
            show['hall'] = seat.select('.hall')[0].get_text()
            show['price'] = parser.parse_price(seat.select('.sellPr .stonefont')[0].get_text())
            shows.append(show)
        return shows

    # def get_mt_price_font_cookies(self, cinema_id):
    #     self.chrome.get("http://m.maoyan.com/shows/" + str(cinema_id))
    #     html = self.chrome.page_source
    #     stone_font = re.search('base64,(.*)\) format', html).group(1)
    #     cookies = dict()
    #     for c in self.chrome.get_cookies():
    #         cookies[c['name']] = c['value']
    #     return [stone_font, cookies]


def mt_m_test():
    from selenium.webdriver.chrome.options import Options
    from selenium import webdriver
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('user-agent="Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Mobile Safari/537.36"')
    chrome = webdriver.Chrome(chrome_options=chrome_options)
    chrome.implicitly_wait(5)
    mt = MTPriceMiddleware()
    shows = mt.get_movie_shows('http://m.maoyan.com/shows/6', chrome)
    print(shows)


if __name__ == '__main__':
    mt_m_test()

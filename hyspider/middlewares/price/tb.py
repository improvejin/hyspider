import json
from datetime import date

from selenium.webdriver import TouchActions

from hyspider.middlewares.browser import BrowserMiddleware


class TBPriceMiddleware(BrowserMiddleware):

    def get_response_content(self, chrome):
        movie_shows = list()

        posters = chrome.find_elements_by_css_selector('.swiper-slide')
        index = 0
        for poster in posters:
            # 不能用click, tb h5不捕获click event
            if index != 0:
                # 第一个已经是active,不能再tap,每次tap后dom会变，需构建新的action, 否则会报异常
                action = TouchActions(chrome)
                action.tap(poster).perform()
            index += 1
            self.show_all_price(chrome)
            self.wait_visible_by_class(chrome, 'schedule-container')
            movie = dict()
            movie['movie_id'] = poster.get_attribute('data-showid')
            movie['shows'] = list()

            schedule_list = chrome.find_elements_by_class_name('schedules-list')
            for schedule in schedule_list:
                ts = int(schedule.get_attribute('data-schedule'))
                show_date = date.fromtimestamp(ts/1000).isoformat()
                seats = schedule.find_elements_by_tag_name('a')
                for seat in seats:
                    show = dict()
                    show['show_date'] = show_date
                    show['begin'] = seat.find_element_by_class_name('item-clock').text
                    show['end'] = seat.find_element_by_class_name('item-end').text[0:-2]
                    show['price'] = seat.find_element_by_class_name('price').text
                    show['language'] = seat.find_element_by_class_name('item-type').text
                    show['hall'] = seat.find_element_by_class_name('item-hall').text
                    movie['shows'].append(show)
            movie_shows.append(movie)
            self.hidde_element_by_class(chrome, 'schedule-container')
        return json.dumps(movie_shows)

    def show_all_price(self, chrome):
        js = 'var eles = document.getElementsByClassName("schedule-container"); for(var i = 0;i<eles.length;i++) eles[i].className+=" show";'
        chrome.execute_script(js)

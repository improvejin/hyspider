
from hyspider.middlewares.browser import BrowserMiddleware


class CityTBMiddleware(BrowserMiddleware):

    def get_response_content(self, chrome):
        city_node = chrome.find_element_by_class_name('cityWrap')
        city_node.click()
        self.wait_visible_by_class(chrome, 'M-cityList')
        return chrome.page_source

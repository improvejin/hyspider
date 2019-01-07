import scrapy
from selenium.webdriver.chrome.options import Options
from selenium import webdriver

from hyspider.utils import proxy


class BrowserSpider(scrapy.Spider):
    chrome_options = Options()
    chrome = None

    custom_settings = {
        'DOWNLOADER_MIDDLEWARES': {'hyspider.middlewares.browser.BrowserMiddleware': 543}
    }

    def __init__(self):
        self.custom_browser_options()
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument('--disable-gpu')
        # self.chrome_options.add_argument("--proxy-server=http://" + proxy.get_random_ip_port())
        self.chrome = webdriver.Chrome(chrome_options=self.chrome_options)
        self.chrome.implicitly_wait(5)  #必须进行设置，海报poster通过ajax加载改变stone_font

    def custom_browser_options(self):
        pass

    def close(self, reason):
        self.chrome.quit()

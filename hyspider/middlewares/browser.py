import time
from scrapy import signals
from scrapy.http import TextResponse
from selenium.webdriver import DesiredCapabilities, Proxy
from selenium.webdriver.common.by import By
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


class BrowserMiddleware(object):
    # visibility:hidden 比display:none高效
    script = 'var eles = document.getElementsByClassName("{}"); for(var i = 0;i<eles.length;i++) eles[i].style.display="none";'

    @classmethod
    def from_crawler(cls, crawler):
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        desired_capabilities = DesiredCapabilities.CHROME.copy()
        proxy = Proxy(
            {
                'proxyType': ProxyType.MANUAL,
                'httpProxy': 'ip:port'  # 代理ip和端口
            }
        )
        # proxy.add_to_capabilities(desired_capabilities)
        # spider.chrome.start_session(desired_capabilities)
        spider.chrome.get(request.url)
        content = self.get_response_content(spider.chrome)
        windows = spider.chrome.window_handles
        if len(windows) > 1:
            spider.chrome.close()
        body = content.encode('utf-8')
        response = TextResponse(url=request.url, request=request, body=body)
        return response

    def process_response(self, request, response, spider):
        return response

    def process_exception(self, request, exception, spider):
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

    def get_response_content(self, chrome):
        return chrome.page_source

    def wait_visible_by_class(self, parent, tag_cls):
        WebDriverWait(parent, 5).until(expected_conditions.visibility_of_all_elements_located((By.CLASS_NAME, tag_cls)))

    def wait_clickable_by_class(self, parent, tag_cls):
        WebDriverWait(parent, 5).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, tag_cls)))

    # 解决页面切换的问题
    def hidde_element_by_class(self, chrome, tag_cls):
        js = self.script.format(tag_cls)
        chrome.execute_script(js)

    def wait_active_by_class(self, parent, ele, tag_cls):
        active = parent.find_element_by_class_name(tag_cls)
        c = 0
        while c < 10 and active != ele:
            time.sleep(0.5)
            active = parent.find_element_by_class_name(tag_cls)
            c += 1
        assert active == ele
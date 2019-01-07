import scrapy

from hyspider.spiders.browser import BrowserSpider


class IPProxyTestSpider(BrowserSpider):
    name = 'proxy_test'
    allowed_domains = ['icanhazip.com']

    # custom_settings = {
    #     'DOWNLOADER_MIDDLEWARES': {
    #         'hyspider.middlewares.ipproxy.ProxyMiddleware': 100,
    #         'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    #         'hyspider.middlewares.useragent.random.UserAgentRandomMiddleware': 400
    #     }
    # }

    def start_requests(self):
        yield scrapy.Request(url="http://icanhazip.com/", callback=self.parse)

    def parse(self, response):
        print(response.text)
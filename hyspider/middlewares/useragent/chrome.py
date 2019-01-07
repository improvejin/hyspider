from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware


class ChromeMiddleware(UserAgentMiddleware):
    user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'

    def __init__(self):
        super().__init__(self.user_agent)

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        return o
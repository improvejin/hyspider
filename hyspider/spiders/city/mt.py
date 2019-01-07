from hyspider.items.city import CityMT
from hyspider.spiders.browser import BrowserSpider


class CityMTSpider(BrowserSpider):
    """
    需继承BrowserSpider, maoyan city是通过ajax加载的, 也可用splash
    """
    name = 'city_mt'
    allowed_domains = ['maoyan.com']
    start_urls = ['http://maoyan.com']

    def parse(self, response):
        groups = response.css('.city-list li')
        for group in groups:
            g = group.css('span::text').extract()[0]
            cities = group.css('a')
            for city in cities:
                c = CityMT()
                c['id'] = city.css('::attr(data-ci)').extract()[0]
                c['g'] = g
                c['name'] = city.css('::text').extract()[0]
                yield c


        # bs = BeautifulSoup(text)
        # groups = bs.findAll('li')
        # for group in groups:
        #     c['group'] = group.find("span").get_text()
        #     cities = group.select('a')
        #     for city in cities:
        #         c['id'] = int(city.attrs['data-ci'])
        #         c['name'] = city.get_text()
        #         yield c


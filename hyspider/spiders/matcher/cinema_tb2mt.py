import scrapy

from hyspider.items.cinema import CinemaTB
from hyspider.manager.cinema import CinemaManager


class MatcherSpider(scrapy.Spider):

    name = 'cinema_tb2mt'
    allowed_domains = ['maoyan.com']
    start_urls = ['http://maoyan.com']

    custom_settings = {
        'ITEM_PIPELINES': {
            'hyspider.pipelines.matcher.MatcherPipeline': 300,
            'hyspider.pipelines.persistence.PersistencePipeline': 800,
        }
    }

    def parse(self, response):
        manager = CinemaManager.get_instance()
        unmatched_cinemas_tb = manager.load_unmatched_cinema(CinemaTB)
        for cinema_tb in unmatched_cinemas_tb:
            yield cinema_tb
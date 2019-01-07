from scrapy import Field

from hyspider.items.base import MovieBase
from hyspider.items.channel import ChannelTB, ChannelMT, ChannelLM, ChannelDB


class MovieTB(MovieBase, ChannelTB):
    @classmethod
    def get_spider_name(cls):
        return 'movie_tb'


class MovieMT(MovieBase, ChannelMT):
    @classmethod
    def get_spider_name(cls):
        return 'movie_mt'


class MovieLM(MovieBase, ChannelLM):
    @classmethod
    def get_spider_name(cls):
        return 'movie_lm'


class MovieDB(MovieBase, ChannelDB):
    type = Field()
    duration = Field()

    @classmethod
    def get_spider_name(cls):
        return 'movie_db'

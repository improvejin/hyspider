from hyspider.items.base import PriceBase
from hyspider.items.channel import ChannelTB, ChannelMT, ChannelLM
from hyspider.items.cinema import CinemaTB, CinemaMT, CinemaLM


class PriceTB(PriceBase, ChannelTB):
    @classmethod
    def get_cinema_cls(cls):
        return CinemaTB

    @classmethod
    def get_spider_name(cls):
        return 'price_tb2'


class PriceMT(PriceBase, ChannelMT):
    @classmethod
    def get_cinema_cls(cls):
        return CinemaMT

    @classmethod
    def get_spider_name(cls):
        return 'price_mt2'


class PriceLM(PriceBase, ChannelLM):
    @classmethod
    def get_cinema_cls(cls):
        return CinemaLM

    @classmethod
    def get_spider_name(cls):
        return 'price_lm'


class Price(PriceBase):
    @classmethod
    def get_table_name(cls):
        return 'price'

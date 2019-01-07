# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy import Field


class ChannelBase:
    @classmethod
    def get_channel_name(cls):
        pass


class Point:
    def __init__(self, lat, lng):
        self.lat = lat
        self.lng = lng

    def __str__(self):
        return 'Point({}, {})'.format(self.lat, self.lng)


class LatLng(scrapy.Item):
    lat_lng = Field()
    location = Field()  # mysql中Point
    precise = Field()
    confidence = Field()


class CinemaBase(LatLng, ChannelBase):
    id = Field()
    name = Field()
    city = Field()
    district = Field()
    addr = Field()
    phone = Field()
    min_price = Field()

    @classmethod
    def get_table_name(cls):
        return 'cinema_{}'.format(cls.get_channel_name())

    @classmethod
    def get_spider_name(cls):
        return 'cinema_{}'.format(cls.get_channel_name())

    @classmethod
    def get_table_columns(cls):
        instance = cls()
        return instance.fields.keys()

    @classmethod
    def get_table_columns_with_prefix(cls, prefix=None):
        columns = cls.get_table_columns()
        if prefix is None:
            prefix = cls.get_table_name()
        return ['{}.{}'.format(prefix, col) for col in columns]

    @classmethod
    def get_match2mt_result_table_name(cls):
        return 'match_cinema_{}2mt'.format(cls.get_channel_name())


class CinemaMatchResult(scrapy.Item):
    id_mt = Field()
    id_matched = Field()
    match_type = Field()
    match_score = Field()
    match_step = Field()
    is_delete = Field()


class Cinema(scrapy.Item):
    """汇总各个渠道"""
    id_mt = Field()
    id_tb = Field()
    id_lm = Field()

    @classmethod
    def get_table_name(cls):
        return 'cinema'


class CityBase(scrapy.Item, ChannelBase):
    id = Field()
    g = Field()     # 分组group, group是mysql关键字
    name = Field()

    @classmethod
    def get_table_name(cls):
        return 'city_{}'.format(cls.get_channel_name())

    @classmethod
    def get_city_name(cls, city_id):
        from hyspider.utils.db_util import DBUtil
        db = DBUtil.get_instance(True)
        sql = 'select name from {} where id={}'.format(cls.get_table_name(), city_id)
        res = db.exec_query(sql)
        return res[0][0][0]


class City(scrapy.Item):
    id_mt = Field()
    id_tb = Field()
    id_lm = Field()
    g = Field()
    name = Field()
    fly = Field


class MovieBase(scrapy.Item, ChannelBase):
    id = Field()
    name = Field()
    score = Field()
    version = Field()
    poster = Field()
    release_date = Field()
    actors = Field()
    ongoing = Field()

    @classmethod
    def get_table_name(cls):
        return 'movie_{}'.format(cls.get_channel_name())

    @classmethod
    def get_match2db_result_table_name(cls):
        return 'match_movie_{}2db'.format(cls.get_channel_name())

    @classmethod
    def get_spider_name(cls):
        pass


class MovieMatchResult(scrapy.Item):
    id_db = Field()
    id_matched = Field()
    match_type = Field()
    match_score = Field()
    match_step = Field()
    is_delete = Field()


class Movie(scrapy.Item):
    """汇总各个渠道"""
    id_db = Field()
    id_mt = Field()
    id_tb = Field()
    id_lm = Field()

    @classmethod
    def get_table_name(cls):
        return 'movie'


class PriceBase(scrapy.Item, ChannelBase):
    cinema_id = Field()
    movie_id = Field()
    show_date = Field()
    begin = Field()
    end = Field()
    language = Field()
    hall = Field()
    price = Field()

    @classmethod
    def get_table_name(cls):
        return 'price_{}'.format(cls.get_channel_name())

    @classmethod
    def get_cinema_cls(cls):
        pass

    @classmethod
    def get_spider_name(cls):
        pass


class NotificationBase(scrapy.Item):
    cinema_id = Field()
#    update_time = Field()

    # def __init__(self):
    #     self['update_time'] = datetime.now().isoformat()

    @classmethod
    def get_table_name(cls):
        return 'cinema_{}'.format(cls.get_channel_name())


class PriceUpdateStatus(scrapy.Item):
    city = Field()
    price_update_time = Field()
    price_match_time = Field()
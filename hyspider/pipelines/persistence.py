from datetime import datetime

from hyspider import settings
from hyspider.items.base import NotificationBase, PriceBase, Cinema, Movie, CinemaBase
from hyspider.utils.db_util import DBUtil


class PersistencePipeline(object):

    cinema_tb2mt = dict()
    cinema_lm2mt = dict()
    movie_mt2db = dict()
    movie_tb2db = dict()
    movie_lm2db = dict()

    def __init__(self):
        self.db = DBUtil.get_instance()

    @classmethod
    def from_crawler(cls, crawler):
        return cls()

    def open_spider(self, spider):
        self.load_cinema_and_movie()

    def close_spider(self, spider):
        pass

    def load_cinema_and_movie(self):
        cinema_sql = 'select id_mt, id_tb, id_lm from {}'.format(Cinema.get_table_name())
        cinemas = self.db.to_item_from_query(cinema_sql, Cinema)
        for cinema in cinemas:
            self.cinema_tb2mt[cinema['id_tb']] = cinema['id_mt']
            self.cinema_lm2mt[cinema['id_lm']] = cinema['id_mt']
        movie_sql = 'select id_db, id_mt, id_tb, id_lm from {}'.format(Movie.get_table_name())
        movies = self.db.to_item_from_query(movie_sql, Movie)
        for movie in movies:
            self.movie_mt2db[movie['id_mt']] = movie['id_db']
            self.movie_tb2db[movie['id_tb']] = movie['id_db']
            self.movie_lm2db[movie['id_lm']] = movie['id_db']

    def process_item(self, item, spider):
        item_class = item.__class__
        if settings.UPDATE_PRICE and issubclass(item_class, PriceBase):
            self.process_price_item(item)
        elif settings.UPDATE_MIN_PRICE and issubclass(item_class, CinemaBase):
            sql = 'update {} set price = {} where id = {}'.format(item_class.get_table_name(), item['price'], item['id'])
            self.db.exec_update(sql)
        elif issubclass(item_class, NotificationBase):
            sql = 'update {} set price_update_time = "{}" where id = {}'.format(item_class.get_table_name(), datetime.now().strftime('%Y-%m-%d %H:%M:%S'), item['cinema_id'])
            self.db.exec_update(sql)
        else:
            self.db.save(item, item_class.get_table_name())

    def process_price_item(self, item):
        """直接更新price表"""
        channel = item.get_channel_name()
        if channel == 'mt':
            cinema_id = item['cinema_id']
            movie_id = self.movie_mt2db.get(item['movie_id'], 0)
        elif channel == 'tb':
            cinema_id = self.cinema_tb2mt.get(item['cinema_id'], 0)
            movie_id = self.movie_tb2db.get(item['movie_id'], 0)
        elif channel == 'lm':
            cinema_id = self.cinema_lm2mt.get(item['cinema_id'], 0)
            movie_id = self.movie_lm2db.get(item['movie_id'], 0)
        if cinema_id != 0 and movie_id != 0:
            sql = """insert into price(cinema_id, movie_id, show_date, begin, end, language, hall, price_{})
             values({}, {}, '{}', '{}', '{}', '{}', '{}', {}) on duplicate key update price_{} = {}""".format(
                channel, cinema_id, movie_id, item['show_date'], item['begin'], item['end'], item['language'],
                item['hall'], item['price'], channel, item['price'])
            self.db.exec_update(sql)
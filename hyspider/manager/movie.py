from hyspider.items.base import MovieMatchResult
from hyspider.items.movie import MovieDB
from hyspider.utils.db_util import DBUtil


class MovieManager(object):

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        else:
            obj = cls()
            cls._instance = obj
            return obj

    def __init__(self):
        self.db = DBUtil()

    def get_db(self):
        return self.db

    def match_db_movie_by_name(self, channel_movie_cls, step):
        """与豆瓣电影通过电影名匹配"""
        sql = '''select t1.id as id_db, t2.id as id_matched, 4 as match_type, 1 as match_score, {} as match_step, 0 as is_delete
                from {} t1 join {} t2
                on (t1.name = t2.name) '''.format(step, MovieDB.get_table_name(),  channel_movie_cls.get_table_name())
        return self.db.to_item_from_query(sql, MovieMatchResult)

    def save_match_result(self, channel_movie_cls, match_results):
        for matched_item in match_results:
            self.db.save(matched_item, channel_movie_cls.get_match2db_result_table_name())

    def save_channels_match_results(self):
        """豆瓣的电影可能没有与所有的渠道都匹配上,所以用left join"""
        sql = '''replace into movie(id_db,id_mt,id_tb,id_lm,name,actors,type,score,duration,poster,release_date,ongoing)
                select t1.id as id_db,  COALESCE(t2.id_matched, 0) as id_mt, COALESCE(t3.id_matched, 0) as id_tb, 
                COALESCE(t4.id_matched, 0) as id_lm,  
                t1.name,t1.actors, t1.type, t1.score, t1.duration, t1.poster, t1.release_date, t1.ongoing
                from movie_db t1 
                left join match_movie_mt2db t2 on (t1.id=t2.id_db)
                left join match_movie_tb2db t3 on (t1.id=t3.id_db)
                left join match_movie_lm2db t4 on (t1.id=t4.id_db)'''
        self.db.exec_update(sql)
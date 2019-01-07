import logging
import threading
from datetime import datetime

from hyspider.items.base import CinemaBase, CinemaMatchResult, City
from hyspider.items.cinema import CinemaMT, CinemaLM, CinemaTB
from hyspider.utils.db_util import DBUtil
from hyspider.utils.text_matcher import TextMatcher
from hyspider import constants

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class CinemaManager(object):

    logger = logging.getLogger(__name__)

    _instance = None

    lock = threading.Lock()

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        else:
            obj = cls()
            cls._instance = obj
            return obj

    def __init__(self):
        self.db = DBUtil(True)

    def get_db(self):
        return self.db

    def load_matched_cinema_by_phone(self, item_class, city, step):
        sql = '''select t1.id as id_mt, t2.id as id_matched, 1 as match_type, 1 as match_score, {} as match_step, 0 as is_delete
                from {} t1 join {} t2
                on (t1.city = '{}' and t2.city = '{}') and
                (
                    (t1.phone = t2.phone) 
                    or (INSTR(t1.addr,t2.addr)>0 or INSTR(t2.addr,t1.addr)>0)
                    or ((INSTR(t1.name,t2.name)>0 or INSTR(t2.name,t1.name)>0) and t1.district=t2.district)
                )'''.format(step, CinemaMT.get_table_name(),  item_class.get_table_name(), city, city)
        return self.db.to_item_from_query(sql, CinemaMatchResult)

    def load_unmatched_cinema(self, item_class, city):
        assert issubclass(item_class, CinemaBase) is True
        sql = '''select {} from {} t1 left join {} t2 on t1.id = t2.id_matched and t2.is_delete=0
             where t1.city='{}' and  t2.id_matched is null'''.format(','.join(item_class.get_table_columns_with_prefix('t1')),
                                           item_class.get_table_name(), item_class.get_match2mt_result_table_name(), city)
        return self.db.to_item_from_query(sql, item_class)

    def load_cinema(self, item_class, where_condition=None):
        assert issubclass(item_class, CinemaBase) is True
        # python中无块级作用域
        if where_condition is not None:
            sql = 'select {} from {} where {}'.format(','.join(item_class.get_table_columns()),
                                                      item_class.get_table_name(),
                                                      where_condition)
        else:
            sql = 'select {} from {}'.format(','.join(item_class.get_table_columns()), item_class.get_table_name())
        return self.db.to_item_from_query(sql, item_class)

    def _remove_cinema_match(self, table, id_mt, id_matched, match_score, step):
        sql = 'update {} set is_delete = 1, match_score = {}, match_step = {} where id_mt = {} and id_matched = {}'.format(table, match_score, step, id_mt, id_matched)
        self.db.exec_update(sql)

    def _remove_invalid_match_by_sql(self, cinema_cls, sql, step):
        """通过地址检查删除无效匹配"""
        rows = self.db.exec_query(sql)[0]
        text_matcher = TextMatcher()
        for row in rows:
            cinema_mt = self.load_cinema(CinemaMT, 'id={}'.format(row[0]))[0]
            cinema_matched = self.load_cinema(cinema_cls, 'id={}'.format(row[1]))[0]
            match_score = text_matcher.sim(cinema_mt['addr'], cinema_matched['addr'])
            if match_score < constants.VALID_ADDRESS_MATCH_SCORE_ON_DELETE:
                self.logger.debug('cinema_mt({},{}) invalid matched with {}({}, {})'.format(row[0], cinema_mt['addr'], cinema_cls.get_table_name(),  row[1], cinema_matched['addr']))
                self._remove_cinema_match(cinema_cls.get_match2mt_result_table_name(), row[0], row[1], match_score, step)

    def remove_invalid_match(self, cinema_cls, step):
        # remove duplicate id_matched
        matched_table = cinema_cls.get_match2mt_result_table_name()
        # group cat
        sql = '''select id_mt, id_matched from {}
                    where is_delete=0 and id_matched in 
                    (
                    select id_matched from 
                    {}
                    where is_delete=0
                    group by id_matched
                    having count(*)>1
                    )
                '''.format(matched_table, matched_table)
        self._remove_invalid_match_by_sql(cinema_cls, sql, step)
        # remove duplicate id_mt
        sql = '''select id_mt, id_matched from {}
                    where is_delete=0 and id_mt in 
                    (
                    select id_mt from 
                    {}
                    where is_delete=0
                    group by id_mt
                    having count(*)>1
                    )
                '''.format(matched_table, matched_table)
        self._remove_invalid_match_by_sql(cinema_cls, sql, step)

    def load_cinema_ids(self, cinema_cls, filter_condition='1=1'):
        return self.db.load_ids(cinema_cls.get_table_name(), filter_condition)

    def need_update_cinema_ids(self, cinema_cls, city_name):
        today = datetime.now().strftime("%Y-%m-%d")
        rs = self.load_cinema_ids(cinema_cls, 'city="{}" and price_update_time<"{}"'.format(city_name, today))
        return rs

    def exists_all_channels(self, id_mt, id_tb, id_lm):
        sql = 'select * from cinema where id_mt={} and id_tb={} and id_lm={}'.format(id_mt, id_tb, id_lm)
        rows = self.db.exec_query(sql)[0]
        return len(rows) == 1

    def save_all_channels(self, id_mt, id_tb, id_lm):
        sql = 'replace into cinema(id_mt,id_tb,id_lm) values({}, {}, {})'.format(id_mt, id_tb, id_lm)
        self.db.exec_update(sql)

    def load_match(self, cinema_cls, city):
        sql = '''select id_mt, id_matched, match_score from 
                {} t1 join {} t2 on (t1.city='{}' and t2.is_delete=0 and t1.id=t2.id_matched)
                order by id_mt, match_score desc
        '''.format(cinema_cls.get_table_name(), cinema_cls.get_match2mt_result_table_name(), city)
        d = dict()
        rows = self.db.exec_query(sql)[0]
        for row in rows:
            score = d.get(row[0], (0, 0))[1]
            if row[2] > score:
                d[row[0]] = (row[1], row[2])
        return d

    def mach_all_channels(self, city):
        """
        match_cinema_lm2mt与match_cinema_tb2mt按id_mt full join,
        match_cinema表中id_mt可能重复，需要按id_mt, match_score desc排序去重
        """
        d = dict()
        lm_match = self.load_match(CinemaLM, city)
        tb_match = self.load_match(CinemaTB, city)
        for id_mt, id_matched in tb_match.items():
            d[id_mt] = (id_matched[0], lm_match.get(id_mt, (0, 0))[0])
        for id_mt, id_matched in lm_match.items():
            if id_mt not in d:
                d[id_mt] = (0, id_matched[0])
        for id_mt, id_matched in d.items():
            self.save_all_channels(id_mt, id_matched[0], id_matched[1])

        self.update_cinema_info()

    def update_cinema_info(self):
        sql = """
            update cinema join cinema_mt on (cinema.id_mt = cinema_mt.id and cinema.name='')
            set cinema.name = cinema_mt.name, cinema.city = cinema_mt.city, cinema.district = cinema_mt.district,cinema.addr = cinema_mt.addr,
            cinema.lat_lng = cinema_mt.lat_lng, cinema.location = cinema_mt.location;
        """
        self.db.exec_update(sql)

    def get_cinema_city_id(self, city_name):
        sql = """select id_mt,id_tb,id_lm from city where name = '{}' """.format(city_name)
        return self.db.to_item_from_query(sql, City)[0]


if __name__ == '__main__':
    pass
    # manager = CinemaManager.get_instance()
    # unmatched_cinemas_tb = manager.load_unmatched_cinema(CinemaLM)
    # cinemas = manager.load_cinema(CinemaLM, 'district=""')
    # for cinema in cinemas:
    #     cinema['district'] = get_district_from_lat_lng(cinema['lat_lng'])
    #     sql = 'update cinema_lm set district="{}" where id={}'.format(cinema['district'], cinema['id'])
    #     manager.get_db().exec_update(sql)

from datetime import datetime, timedelta

from hyspider.utils.log import logger
from hyspider.utils.db_util import DBUtil


class PriceManager(object):

    _instance = None

    @classmethod
    def get_instance(cls):
        if cls._instance:
            return cls._instance
        else:
            obj = cls()
            cls._instance = obj
            return obj

    @classmethod
    def clone(cls):
        return cls()

    def __init__(self):
        self.db = DBUtil(True)

    def remove_expire_price(self, price_cls):
        today = datetime.now().strftime("%Y-%m-%d")
        sql = 'delete from {} where show_date<"{}"'.format(price_cls.get_table_name(), today)
        self.db.exec_update(sql)

    def save_all_channels_price(self, city_name):
        """
        各渠道电影、电影院可能没有匹配成功，渠道也有能没有电影、电影院、电影售价信息
        hive形式sql，mysql无full outer join, 只能使用left join union right join 导致下面执行复杂的sql
        replace into price(cinema_id, movie_id, show_date, begin, end, language, hall,  price_mt, price_tb, price_lm)
        select
        COALESCE(mt_price_tmp.cinema_id, tb_price_tmp.cinema_id, lm_price_tmp.cinema_id) as cinema_id,
        COALESCE(mt_price_tmp.movie_id, tb_price_tmp.movie_id, lm_price_tmp.movie_id) as movie_id,
        COALESCE(mt_price_tmp.show_date, tb_price_tmp.show_date, lm_price_tmp.show_date) as show_date,
        COALESCE(mt_price_tmp.begin, tb_price_tmp.begin, lm_price_tmp.begin) as begin,
        COALESCE(mt_price_tmp.end, tb_price_tmp.end, lm_price_tmp.end) as end,
        COALESCE(mt_price_tmp.language, tb_price_tmp.language, lm_price_tmp.language) as language,
        COALESCE(mt_price_tmp.hall, tb_price_tmp.hall, lm_price_tmp.hall) as hall,
        COALESCE(mt_price_tmp.price, 0) as price_mt,
        COALESCE(tb_price_tmp.price, 0) as price_tb,
        COALESCE(lm_price_tmp.price, 0) as price_lm
        from
        (
            select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
            from cinema join price_mt on ( cinema.id_mt=price_mt.cinema_id) join movie on (movie.id_mt=price_mt.movie_id)
        ) mt_price_tmp
        full outer join
        (
            select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
            from cinema join price_tb on ( cinema.id_tb=price_tb.cinema_id) join movie on (movie.id_tb=price_tb.movie_id)
        ) tb_price_tmp on (mt_price_tmp.cinema_id = tb_price_tmp.cinema_id and mt_price_tmp.movie_id = tb_price_tmp.movie_id
        and mt_price_tmp.show_date = tb_price_tmp.show_date and mt_price_tmp.begin = tb_price_tmp.begin)
        full outer join
        (
            select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
            from cinema join price_lm on ( cinema.id_lm=price_lm.cinema_id) join movie on (movie.id_lm=price_lm.movie_id)
        ) lm_price_tmp on (COALESCE(mt_price_tmp.cinema_id, tb_price_tmp.cinema_id) = lm_price_tmp.cinema_id and COALESCE(mt_price_tmp.movie_id, tb_price_tmp.movie_id) = lm_price_tmp.movie_id
         and COALESCE(mt_price_tmp.show_date, tb_price_tmp.show_date) = lm_price_tmp.show_date and COALESCE(mt_price_tmp.begin, tb_price_tmp.begin) = lm_price_tmp.begin)

        --------------------------------------------------------------------------------------
        下面sql可查出电影在各个渠道同一个影院都有售卖时的价格信息，于上面sql将full join替换为 join时等价
        replace into  price(movie_id, cinema_id, show_date, begin, end, language, hall,  price_mt, price_tb, price_lm)
        select t1.id_db as movie_id, t5.id_mt as cinema_id, t3.show_date as show_date, t3.begin as begin,
        t3.end as end, t3.language as language, t3.hall as hall,
        t3.price as price_mt, t4.price as price_tb, t2.price as price_lm
        from movie t1
        join price_lm t2 on t1.id_lm = t2.movie_id
        join price_mt t3 on t1.id_mt = t3.movie_id
        join price_tb t4 on t1.id_tb = t4.movie_id
        join cinema t5 on (t2.cinema_id = t5.id_lm and t3.cinema_id=t5.id_mt and t4.cinema_id=t5.id_tb
        and t2.show_date=t3.show_date and t2.show_date=t4.show_date
        and t2.begin = t3.begin and t2.begin=t4.begin)
        """
        sql = '''
            replace into price(cinema_id, movie_id, show_date, begin, end, language, hall,  price_mt, price_tb, price_lm)
            select
            COALESCE(mt_cinema_id, tb_cinema_id, lm_cinema_id) as cinema_id,
            COALESCE(mt_movie_id, tb_movie_id, lm_movie_id) as movie_id,
            COALESCE(mt_show_date, tb_show_date, lm_show_date) as show_date,
            COALESCE(mt_begin, tb_begin, lm_begin) as begin,
            COALESCE(mt_end, tb_end, lm_end) as end,
            COALESCE(mt_language, tb_language, lm_language) as language,
            COALESCE(mt_hall, tb_hall, lm_hall) as hall,
            COALESCE(mt_price, 10000) as price_mt,
            COALESCE(tb_price, 10000) as price_tb,
            COALESCE(lm_price, 10000) as price_lm
            from 
            (
                select mt_price_tmp.cinema_id as mt_cinema_id, mt_price_tmp.movie_id as mt_movie_id,
                mt_price_tmp.show_date as mt_show_date, mt_price_tmp.begin as mt_begin, 
                mt_price_tmp.end as mt_end, mt_price_tmp.language as mt_language, 
                mt_price_tmp.hall as mt_hall, mt_price_tmp.price as mt_price,
                tb_price_tmp.cinema_id as tb_cinema_id, tb_price_tmp.movie_id as tb_movie_id,
                tb_price_tmp.show_date as tb_show_date, tb_price_tmp.begin as tb_begin, 
                tb_price_tmp.end as tb_end, tb_price_tmp.language as tb_language, 
                tb_price_tmp.hall as tb_hall, tb_price_tmp.price as tb_price
                from 
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_mt on ( cinema.id_mt=price_mt.cinema_id) join movie on (movie.id_mt=price_mt.movie_id)
                ) mt_price_tmp
                left join
                (
                     select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                     from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                     join price_tb on ( cinema.id_tb=price_tb.cinema_id) join movie on (movie.id_tb=price_tb.movie_id)
                ) tb_price_tmp on (mt_price_tmp.cinema_id = tb_price_tmp.cinema_id and mt_price_tmp.movie_id = tb_price_tmp.movie_id
                and mt_price_tmp.show_date = tb_price_tmp.show_date and mt_price_tmp.begin = tb_price_tmp.begin)
             
                union  all
             
                select mt_price_tmp.cinema_id as mt_cinema_id, mt_price_tmp.movie_id as mt_movie_id,
                mt_price_tmp.show_date as mt_show_date, mt_price_tmp.begin as mt_begin, 
                mt_price_tmp.end as mt_end, mt_price_tmp.language as mt_language, 
                mt_price_tmp.hall as mt_hall, mt_price_tmp.price as mt_price,
                tb_price_tmp.cinema_id as tb_cinema_id, tb_price_tmp.movie_id as tb_movie_id,
                tb_price_tmp.show_date as tb_show_date, tb_price_tmp.begin as tb_begin, 
                tb_price_tmp.end as tb_end, tb_price_tmp.language as tb_language, 
                tb_price_tmp.hall as tb_hall, tb_price_tmp.price as tb_price
                from 
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_mt on ( cinema.id_mt=price_mt.cinema_id) join movie on (movie.id_mt=price_mt.movie_id)
                ) mt_price_tmp
                right join
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_tb on ( cinema.id_tb=price_tb.cinema_id) join movie on (movie.id_tb=price_tb.movie_id)
                ) tb_price_tmp on (mt_price_tmp.cinema_id = tb_price_tmp.cinema_id and mt_price_tmp.movie_id = tb_price_tmp.movie_id
                and mt_price_tmp.show_date = tb_price_tmp.show_date and mt_price_tmp.begin = tb_price_tmp.begin)
                where mt_price_tmp.cinema_id is null
            ) mt_tb_price_tmp left join 
            (
                select cinema.id_mt as lm_cinema_id, movie.id_db as lm_movie_id, show_date as lm_show_date, begin as lm_begin, 
                                            end as lm_end, language as lm_language, hall as lm_hall, price as lm_price
                from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                join price_lm on ( cinema.id_lm=price_lm.cinema_id) join movie on (movie.id_lm=price_lm.movie_id)
            ) lm_price_tmp
            on (COALESCE(mt_tb_price_tmp.mt_cinema_id, mt_tb_price_tmp.tb_cinema_id) = lm_price_tmp.lm_cinema_id 
            and COALESCE(mt_tb_price_tmp.mt_movie_id, mt_tb_price_tmp.mt_movie_id) = lm_price_tmp.lm_movie_id
            and COALESCE(mt_tb_price_tmp.mt_show_date, mt_tb_price_tmp.tb_show_date) = lm_price_tmp.lm_show_date 
            and COALESCE(mt_tb_price_tmp.mt_begin, mt_tb_price_tmp.tb_begin) = lm_price_tmp.lm_begin)

            union all

            select
            COALESCE(mt_cinema_id, tb_cinema_id, lm_cinema_id) as cinema_id,
            COALESCE(mt_movie_id, tb_movie_id, lm_movie_id) as movie_id,
            COALESCE(mt_show_date, tb_show_date, lm_show_date) as show_date,
            COALESCE(mt_begin, tb_begin, lm_begin) as begin,
            COALESCE(mt_end, tb_end, lm_end) as end,
            COALESCE(mt_language, tb_language, lm_language) as language,
            COALESCE(mt_hall, tb_hall, lm_hall) as hall,
            COALESCE(mt_price, 10000) as price_mt,
            COALESCE(tb_price, 10000) as price_tb,
            COALESCE(lm_price, 10000) as price_lm
            from 
            (
                select mt_price_tmp.cinema_id as mt_cinema_id, mt_price_tmp.movie_id as mt_movie_id,
                mt_price_tmp.show_date as mt_show_date, mt_price_tmp.begin as mt_begin, 
                mt_price_tmp.end as mt_end, mt_price_tmp.language as mt_language, 
                mt_price_tmp.hall as mt_hall, mt_price_tmp.price as mt_price,
                tb_price_tmp.cinema_id as tb_cinema_id, tb_price_tmp.movie_id as tb_movie_id,
                tb_price_tmp.show_date as tb_show_date, tb_price_tmp.begin as tb_begin, 
                tb_price_tmp.end as tb_end, tb_price_tmp.language as tb_language, 
                tb_price_tmp.hall as tb_hall, tb_price_tmp.price as tb_price
                from 
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_mt on ( cinema.id_mt=price_mt.cinema_id) join movie on (movie.id_mt=price_mt.movie_id)
                ) mt_price_tmp
                left join
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_tb on ( cinema.id_tb=price_tb.cinema_id) join movie on (movie.id_tb=price_tb.movie_id)
                ) tb_price_tmp on (mt_price_tmp.cinema_id = tb_price_tmp.cinema_id and mt_price_tmp.movie_id = tb_price_tmp.movie_id
                and mt_price_tmp.show_date = tb_price_tmp.show_date and mt_price_tmp.begin = tb_price_tmp.begin)
             
                union  all
             
                select mt_price_tmp.cinema_id as mt_cinema_id, mt_price_tmp.movie_id as mt_movie_id,
                mt_price_tmp.show_date as mt_show_date, mt_price_tmp.begin as mt_begin, 
                mt_price_tmp.end as mt_end, mt_price_tmp.language as mt_language, 
                mt_price_tmp.hall as mt_hall, mt_price_tmp.price as mt_price,
                tb_price_tmp.cinema_id as tb_cinema_id, tb_price_tmp.movie_id as tb_movie_id,
                tb_price_tmp.show_date as tb_show_date, tb_price_tmp.begin as tb_begin, 
                tb_price_tmp.end as tb_end, tb_price_tmp.language as tb_language, 
                tb_price_tmp.hall as tb_hall, tb_price_tmp.price as tb_price
                from 
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_mt on ( cinema.id_mt=price_mt.cinema_id) join movie on (movie.id_mt=price_mt.movie_id)
                ) mt_price_tmp
                right join
                (
                    select cinema.id_mt as cinema_id, movie.id_db as movie_id, show_date, begin, end, language, hall, price
                    from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                    join price_tb on ( cinema.id_tb=price_tb.cinema_id) join movie on (movie.id_tb=price_tb.movie_id)
                ) tb_price_tmp on (mt_price_tmp.cinema_id = tb_price_tmp.cinema_id and mt_price_tmp.movie_id = tb_price_tmp.movie_id
                and mt_price_tmp.show_date = tb_price_tmp.show_date and mt_price_tmp.begin = tb_price_tmp.begin)
                where mt_price_tmp.cinema_id is null
            ) mt_tb_price_tmp right join 
            (
                select cinema.id_mt as lm_cinema_id, movie.id_db as lm_movie_id, show_date as lm_show_date, begin as lm_begin, 
                                            end as lm_end, language as lm_language, hall as lm_hall, price as lm_price
                from cinema_mt join cinema on(cinema_mt.city='{}' and cinema_mt.id=cinema.id_mt) 
                join price_lm on ( cinema.id_lm=price_lm.cinema_id) join movie on (movie.id_lm=price_lm.movie_id)
            ) lm_price_tmp
            on (COALESCE(mt_tb_price_tmp.mt_cinema_id, mt_tb_price_tmp.tb_cinema_id) = lm_price_tmp.lm_cinema_id 
            and COALESCE(mt_tb_price_tmp.mt_movie_id, mt_tb_price_tmp.mt_movie_id) = lm_price_tmp.lm_movie_id
            and COALESCE(mt_tb_price_tmp.mt_show_date, mt_tb_price_tmp.tb_show_date) = lm_price_tmp.lm_show_date 
            and COALESCE(mt_tb_price_tmp.mt_begin, mt_tb_price_tmp.tb_begin) = lm_price_tmp.lm_begin)
            where COALESCE(mt_tb_price_tmp.mt_cinema_id, mt_tb_price_tmp.tb_cinema_id) is null
         '''.format(city_name, city_name, city_name, city_name, city_name, city_name, city_name, city_name, city_name, city_name)
        logger.info("city %s, start to match cinema price", city_name)
        self.db.exec_update(sql)
        logger.info("city %s, end to match cinema price", city_name)

    def update_cinema_min_price(self):
        """根据综合所有渠道后的价格表更新影院最低价格,下面sql与执行的sql等价
            update cinema join (
                select cinema_id, min(min_price) as min_price
                from
                (
                    select cinema_id, min(price_mt) as min_price
                    from price
                    group by cinema_id
                    union all
                    select cinema_id, min(price_tb) as min_price
                    from price
                    group by cinema_id
                    union all
                    select cinema_id, min(price_lm) as min_price
                    from price
                    group by cinema_id
                )t
                group by cinema_id
            )cinema_min_price on (cinema.id_mt = cinema_min_price.cinema_id)
            set cinema.min_price = cinema_min_price.min_price
        """
        sql = '''
             update cinema join 
             (
                 select cinema_id, LEAST(mt_min_price,tb_min_price, lm_min_price) as min_price
                 from 
                 (
                     select cinema_id, min(price_mt) as mt_min_price, 
                     min(price_tb) as tb_min_price,
                     min(price_lm) as lm_min_price
                     from  price
                     GROUP BY cinema_id
                 )tmp
             )cinema_min_price on (cinema.id_mt = cinema_min_price.cinema_id)
             set cinema.min_price = cinema_min_price.min_price
         '''
        logger.info("start to update cinema min price")
        self.db.exec_update(sql)
        logger.info("end to update cinema min price")

    def cinema_price_updated_done(self, city_name):
        today = datetime.now().strftime('%Y-%m-%d %H-%M-%S')
        sql = """INSERT INTO price_update_status (city,price_update_time) VALUES ('{}','{}')
        ON DUPLICATE KEY UPDATE price_update_time='{}'""".format(city_name, today, today)
        self.db.exec_update(sql)

    def is_cinema_price_update_done(self, city_name):
        today = datetime.now().strftime('%Y-%m-%d')
        sql = """select price_update_time from price_update_status where city = '{}'""".format(city_name)
        price_update_time = self.db.exec_query(sql)[0][0][0].strftime('%Y-%m-%d')
        return price_update_time >= today

    def cinema_price_match_done(self, city_name, delta=0):
        today = (datetime.now()+timedelta(days=delta)).strftime('%Y-%m-%d %H-%M-%S')
        sql = """update price_update_status set price_match_time='{}' where city = '{}'""".format(today,city_name)
        self.db.exec_update(sql)

    def is_cinema_price_match_done(self, city_name):
        today = datetime.now().strftime('%Y-%m-%d')
        sql = """select price_match_time from price_update_status where city = '{}'""".format(city_name)
        price_match_time = self.db.exec_query(sql)[0][0][0].strftime('%Y-%m-%d')
        return price_match_time >= today

    def get_price_update_status(self):
        msg = ''
        sql = """select city, price_update_time, price_match_time from price_update_status where fly=1"""
        from hyspider.items.base import PriceUpdateStatus
        cities_status = self.db.to_item_from_query(sql, PriceUpdateStatus)
        for status in cities_status:
            msg += '{},{},{}\n'.format(status['city'],
                    status['price_update_time'].strftime('%Y-%m-%d'),status['price_match_time'].strftime('%Y-%m-%d'))
        return msg


if __name__ == '__main__':
    manager = PriceManager.get_instance()
    # manager.cinema_price_updated_done('上海')
    # manager.cinema_price_match_done('上海')
    # manager.cinema_price_match_done('上海', -1)
    # print(manager.is_cinema_price_update_done('上海'))
    # print(manager.is_cinema_price_match_done('上海'))
    # msg = manager.get_price_update_status()
    # print(msg)

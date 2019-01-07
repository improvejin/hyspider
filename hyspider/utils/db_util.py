import pymysql
from hyspider import settings
from hyspider.items.base import Point
from hyspider.utils.log import logger


class DBUtil:

    _instance = None

    @classmethod
    def get_instance(cls, autocommit=False):
        if cls._instance:
            return cls._instance
        else:
            obj = cls(autocommit)
            cls._instance = obj
            return obj

    """应该单例"""
    def __init__(self, autocommit=False):
        self.conn = pymysql.connect(settings.HOST, settings.USER, settings.PWD, settings.DB, autocommit=autocommit)
        self.conn.set_charset('utf8')
        self.cursor = self.conn.cursor()

    def __del__(self):
        self.cursor.close()
        self.conn.close()

    def save(self, item, table=None):
        cls = item.__class__
        if table is None:
            table = cls.get_table_name()
        columns = ''
        values = ''
        for key, value in item.items():
            columns += "{},".format(key)
            if isinstance(value, int) or isinstance(value, float):
                values += "{},".format(value)
            elif isinstance(value, Point):
                values += "{},".format(value)
            elif isinstance(value, str):
                values += "'{}',".format(value)

        sql = 'replace into {}({}) values({})'.format(table.lower(), columns[0:-1], values[0:-1])
        self.exec_update(sql)

    @classmethod
    def _to_items(cls, item_class, titles, rows):
        instances = []
        for row in rows:
            instance = item_class()
            for i in range(len(titles)):
                instance[titles[i][0]] = row[i]
            instances.append(instance)
        return instances

    def to_item_from_query(self, sql, item_cls):
        result = self.exec_query(sql)
        return self._to_items(item_cls, result[1], result[0])

    def exec_update(self, update_sql):
        logger.debug(update_sql)
        self.conn.ping(reconnect=True)
        self.cursor.execute(update_sql)
        self.conn.commit()

    def exec_query(self, query_sql):
        logger.debug(query_sql)
        self.conn.ping(reconnect=True)
        self.cursor.execute(query_sql)
        titles = self.cursor.description
        rows = self.cursor.fetchall()
        # InnoDB storage engine is repeatable read
        # self.conn.commit()
        return [rows, titles]

    def load_ids(self, table, filter_condition='1=1'):
        sql = 'select id from {} where {} '.format(table, filter_condition)
        rows = self.exec_query(sql)[0]
        return [int(row[0]) for row in rows]



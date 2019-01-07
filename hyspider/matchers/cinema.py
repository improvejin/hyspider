# -*- coding: utf-8 -*-
from hyspider.items.base import CinemaBase
from hyspider.items.cinema import CinemaTB, CinemaLM
from hyspider.pipelines.matcher import MatcherPipeline
from hyspider.manager.cinema import CinemaManager
from hyspider.utils.log import logger


class CinemaMatcher:
    """
    1、通过phone匹配，结果不准确可能有两种情况导致：
        error1: phone相同但并不是同一cinema，同一品牌cinema不同地址phone可能相同, 此情况通过step3 AI检测出无效匹配并删除
        error2: 同一cinema不同channel phone可能不同导致匹配不上, 此情况通过step2 AI匹配
    2、通过AI匹配，找出渠道中未匹配上cinema与MT cinema中按区域查找匹配， AI匹配相对比较准确，但是BD有请求速度限制
    3、删除无效匹配(一个id_mt可能匹配了多个id_matched, 一个id_matched也可能匹配了多个id_mt)，通过AI检测地址相似度小于0.85的删除
    4、删除无效匹配后可能出现无匹配的渠道cinema, 此时需重复step2通过AI进行匹配

    总结：初略匹配(phone, AI)->删除无效匹配(AI)->未匹配上的进行AI匹配
    """

    def __init__(self):
        self.manager = CinemaManager.get_instance()
        self.db = self.manager.get_db()
        self.ai_matcher = MatcherPipeline()

    def match_cinema_by_phone(self, cinema_cls, city,  step):
        """通过phone进行初略匹配"""
        logger.info("step %d, begin to match cinema by phone with city %s", step, city)
        matched_result = self.manager.load_matched_cinema_by_phone(cinema_cls, city, step)
        for matched_item in matched_result:
            self.db.save(matched_item, cinema_cls.get_match2mt_result_table_name())
        logger.info("step %d, end to match cinema by phone with city %s", step, city)

    def match_cinema_by_ai(self, cinema_cls, city, step):
        """通过AI进行初略匹配"""
        logger.info("step %d, begin to match cinema by ai with city %s", step, city)
        unmatched_cinemas = self.manager.load_unmatched_cinema(cinema_cls, city)
        for cinema in unmatched_cinemas:
            generator = self.ai_matcher.process_item(cinema, None)
            matched_item = next(generator)
            if matched_item is not None:
                matched_item['match_step'] = step
                self.db.save(matched_item, cinema_cls.get_match2mt_result_table_name())
        logger.info("step %d, end to match cinema by ai with city %s", step, city)

    def remove_invalid_match(self, cinema_cls, city, step):
        """删除无效匹配"""
        logger.info("step %d, begin to remove invalid match with city %s", step, city)
        self.manager.remove_invalid_match(cinema_cls, step)
        logger.info("step %d, end to remove invalid match with city %s", step, city)

    def match_all_channels(self, city):
        logger.info("begin to match all channels with city %s", city)
        self.manager.mach_all_channels(city)
        logger.info("end to match all channels with city %s", city)

    def match_2mt(self, cinema_cls, city):
        assert issubclass(cinema_cls, CinemaBase)
        logger.info("begin to match cinema %s to mt with city %s", cinema_cls.get_channel_name(), city)
        self.match_cinema_by_phone(cinema_cls, city, 1)
        self.match_cinema_by_ai(cinema_cls, city, 2)
        self.remove_invalid_match(cinema_cls, city, 3)
        self.match_cinema_by_ai(cinema_cls, city, 4)
        logger.info("end to match cinema %s to mt with city %s", cinema_cls.get_channel_name(), city)


if __name__ == '__main__':
    city = '南京'
    cinema_matcher = CinemaMatcher()
    cinema_matcher.match_2mt(CinemaTB, city)
    cinema_matcher.match_2mt(CinemaLM, city)
    cinema_matcher.match_all_channels(city)


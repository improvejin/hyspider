from hyspider.items.base import CinemaBase, CinemaMatchResult
from hyspider.items.cinema import CinemaMT
from hyspider.manager.cinema import CinemaManager
from hyspider.utils.text_matcher import TextMatcher

from hyspider import constants


class MatcherPipeline(object):

    def __init__(self):
        self.cinemas_mt = dict()
        self.cinema_manager = CinemaManager.get_instance()
        self.matcher = TextMatcher()

    def process_item(self, cinema, spider):
        assert isinstance(cinema, CinemaBase)
        """通过AI按区域查找匹配"""
        district = cinema['district']
        city = cinema['city']
        if district not in self.cinemas_mt:
            self.cinemas_mt[district] = self.cinema_manager.load_cinema(CinemaMT, 'city="{}" and district="{}"'.format(city, district))
        cinemas_district_mt = self.cinemas_mt.get(district)
        addr_match_max_score = 0
        name_match_max_score = 0
        matched_cinema_by_addr = None
        matched_cinema_by_name = None
        for cinema_mt in cinemas_district_mt:
            addr_match_score = self.matcher.sim(cinema['addr'], cinema_mt['addr'])
            if addr_match_score > addr_match_max_score:
                addr_match_max_score = addr_match_score
                matched_cinema_by_addr = cinema_mt

            name_match_score = self.matcher.sim(cinema['name'], cinema_mt['name'])
            if name_match_score > name_match_max_score:
                name_match_max_score = name_match_score
                matched_cinema_by_name = cinema_mt

        print(cinema['district'], cinema['id'], cinema['name'], cinema['addr'], '\t', end='')

        # 地址没匹配上通过名字匹配
        if addr_match_max_score > constants.VALID_ADDRESS_MATCH_SCORE:
            matched_cinema = matched_cinema_by_addr
            match_score = addr_match_max_score
            match_type = constants.MATCH_BY_ADDR
        elif name_match_max_score > constants.VALID_NAME_MATCH_SCORE:
            matched_cinema = matched_cinema_by_name
            match_score = name_match_max_score
            match_type = constants.MATCH_BY_NAME
        else:
            matched_cinema = None

        # 将匹配结果存入DB
        if matched_cinema is not None:
            print(matched_cinema['id'], matched_cinema['name'], matched_cinema['addr'], match_score, match_type)
            c = CinemaMatchResult()
            c['id_mt'] = matched_cinema['id']
            c['id_matched'] = cinema['id']
            c['match_type'] = match_type
            c['match_score'] = match_score
            c['is_delete'] = 0
            yield c
        else:
            print('no match')
            yield None

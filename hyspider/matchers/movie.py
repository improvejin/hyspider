from hyspider.items.movie import MovieMT, MovieLM, MovieTB
from hyspider.manager.movie import MovieManager


class MovieMatcher:
    """将豆瓣的电影与其他渠道电影进行匹配"""

    def __init__(self):
        self.manager = MovieManager.get_instance()
        self.db = self.manager.get_db()
        # self.ai_matcher = MatcherPipeline()

    # 通过电影名匹配，可能有别名无法完全匹配
    def match_movie_by_name(self, movie_cls, step):
        match_result = self.manager.match_db_movie_by_name(movie_cls, step)
        self.manager.save_match_result(movie_cls, match_result)

    # 将未匹配上的通过ai匹配
    def match_movie_by_ai(self):
        pass

    def match_2db(self, movie_cls):
        self.match_movie_by_name(movie_cls, 1)
        self.match_movie_by_ai()

    def save_all_channels_match_results(self):
        self.manager.save_channels_match_results()


if __name__ == '__main__':
    match = MovieMatcher()
    match.match_2db(MovieMT)
    match.match_2db(MovieTB)
    match.match_2db(MovieLM)
    match.save_all_channels_match_results()
import getopt
import json
import traceback
import os

import requests
import sys
from apscheduler.schedulers.blocking import BlockingScheduler

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hyspider.items.cinema import CinemaMT, CinemaTB, CinemaLM
from hyspider.items.movie import MovieLM, MovieMT, MovieTB, MovieDB
from hyspider.utils.log import logger
from hyspider.items.price import PriceLM, PriceMT, PriceTB, Price
from hyspider.manager.cinema import CinemaManager
from hyspider.manager.price import PriceManager
from hyspider.settings import BOT_NAME, SCRAPYD_SERVER

cities = ['上海', '南京', '武汉', '成都', '深圳', '西安', '杭州', '北京', '合肥', '苏州']

cities = ['上海']


def spider_status(spider, jobid, status, jobs):
    """判断spider的状态"""
    running = jobs[status]
    for r in running:
        if r['spider'] == spider and r['id'] == str(jobid):
            return True
    return False


def list_spider_jobs():
    params = {'project': BOT_NAME}
    rsp = requests.get(SCRAPYD_SERVER + '/listjobs.json', params)
    return json.loads(rsp.text)


def run_spider(spider, city_id, **kwargs):
    """启动spider"""
    jobs = list_spider_jobs()
    if jobs['status'] != 'ok':
        logger.error('scrapyd may not start, fail to start spider %s', spider)
        return

    if len(jobs['running']) > 6:
        logger.error('reach max jobs, fail to start spider %s', spider)
        return

    if spider_status(spider, city_id, 'running', jobs) or spider_status(spider, city_id, 'pending', jobs):
        logger.info('%s %s, is running or pending', spider, city_id)
        return

    data = {'project': BOT_NAME, 'spider': spider, 'jobid': city_id, 'city_id': city_id}
    for k, v in kwargs.items():
        data[k] = v

    rsp = requests.post(SCRAPYD_SERVER + '/schedule.json', data)
    ret = json.loads(rsp.text)
    if ret['status'] == 'ok':
        logger.info('succeed to start spider %s', spider)
    else:
        logger.error('fail to start spider %s', spider)


# @sch.scheduled_job('cron', hour='01', id='update_movies')
def update_movies():
    """更新渠道电影信息"""
    channels = [MovieLM, MovieMT, MovieTB, MovieDB]
    for channel in channels:
        logger.info('%s to be updated', channel.get_table_name())
        run_spider(channel.get_spider_name(), city_id=289)


# @sch.scheduled_job('cron', hour='01', minute='30', id='match_channels_movie')
def match_channels_movie():
    """将更新的渠道电影与豆瓣电影匹配"""
    channels = [MovieLM, MovieMT, MovieTB]
    from hyspider.matchers.movie import MovieMatcher
    matcher = MovieMatcher()
    for channel in channels:
        logger.info('begin to match movie %s to db', channel.get_channel_name())
        matcher.match_2db(channel)
        logger.info('end to match movie %s to db', channel.get_channel_name())
    logger.info('begin to save  match movie result')
    matcher.save_all_channels_match_results()
    logger.info('end to save  match movie result')


def update_city_prices(city_name):
    """
    更新渠道电影价格信息
    InnoDB默认事物级别是repeatable read,防止同一事物中读取的数据前后不一致，即幻读，
    此处需获取cinema表最新状态，每次查询时需开启一个新的事物，即execute_update后要commit或者重新获取CinemaManager
    """
    cinema_manager = CinemaManager.get_instance()
    price_manager = PriceManager.get_instance()
    try:
        city_info = cinema_manager.get_cinema_city_id(city_name)
        done = 0
        channels = [PriceLM, PriceMT, PriceTB]
        for channel in channels:
            ids = cinema_manager.need_update_cinema_ids(channel.get_cinema_cls(), city_name)
            count = len(ids)
            if count > 0:
                city_id = city_info['id_{}'.format(channel.get_channel_name())]
                logger.info('run %s of city %s, %d cinemas need to be updated', channel.get_spider_name(), city_name,
                            count)
                run_spider(channel.get_spider_name(), city_id=city_id)
            else:
                done += 1
                logger.info('table %s of city %s need not to be updated', channel.get_table_name(), city_name)
        if done == 3:
            # 状态未更新时更新状态,手动在price_update_status插入一条城市记录
            if not price_manager.is_cinema_price_update_done(city_name):
                price_manager.cinema_price_updated_done(city_name)
            else:
                logger.info('city %s, channels price status already updated', city_name)
    except Exception as e:
        logger.error("Unexpected Update {} Price Error: {}, {}".format(city_name, e, traceback.format_exc()))


# @sch.scheduled_job('interval', minutes=5, id='update_prices')
def update_prices():
    global cities
    for city in cities:
        update_city_prices(city)


def update_cinema_min_price():
    """更新影院最低价"""
    logger.info('start to update cinema min price')
    price_manager = PriceManager.clone()
    price_manager.update_cinema_min_price()
    logger.info('end to update cinema min price')


def match_city_channels_price(city_name):
    """如果有渠道价格更新，并且所有的渠道都更新完毕则进行所有渠道价格匹配"""
    price_manager = PriceManager.clone()
    if price_manager.is_cinema_price_update_done(city_name):
        if not price_manager.is_cinema_price_match_done(city_name):
            try:
                price_manager.save_all_channels_price(city_name)
                price_manager.cinema_price_match_done(city_name)
            except Exception as e:
                logger.info("Unexpected Match {} Price Error: {}".format(city_name, e))
                price_manager.cinema_price_match_done(city_name, -1)
        else:
            logger.info('city %s, price match status already update', city_name)
    else:
        logger.info('city %s, some channels price do not update done', city_name)


# @sch.scheduled_job('interval', minutes=12, id='match_channels_price')
def match_channels_price():
    global cities
    for city in cities:
        match_city_channels_price(city)


def force_match_city_channels_price(city_name):
    """如果有渠道价格更新，并且所有的渠道都更新完毕则进行所有渠道价格匹配"""
    logger.info('city %s, start to force match channel price and update cinema min price', city_name)
    price_manager = PriceManager.clone()
    price_manager.save_all_channels_price(city_name)
    price_manager.cinema_price_match_done(city_name)
    logger.info('city %s, end to force match channel price and update cinema min price', city_name)


def force_match_channels_price():
    """强制进行价格同步"""
    global cities
    for city in cities:
        force_match_channels_price(city)
    update_cinema_min_price()


# @sch.scheduled_job('cron', hour='0,5', minute='05', id='remove_expire_channel_price')
def remove_expire_channels_price():
    """删除今天之前的电影售价信息"""
    price_manager = PriceManager.get_instance()
    channels = [PriceLM, PriceMT, PriceTB, Price]
    for channel in channels:
        logger.info('%s delete expire price info', channel.get_table_name())
        price_manager.remove_expire_price(channel)


def update_cinemas(city_name):
    cinema_manager = CinemaManager.get_instance()
    city_info = cinema_manager.get_cinema_city_id(city_name)
    channels = [CinemaMT, CinemaTB, CinemaLM]
    for channel in channels:
        logger.info('%s of city %s to be updated', channel.get_table_name(), city_name)
        city_id = city_info['id_{}'.format(channel.get_channel_name())]
        run_spider(channel.get_spider_name(), city_id=city_id)


def match_cinemas(city_name):
    from hyspider.matchers.cinema import CinemaMatcher
    cinema_matcher = CinemaMatcher()
    channels = [CinemaTB, CinemaLM]
    for channel in channels:
        cinema_matcher.match_2mt(channel, city_name)
    cinema_matcher.match_all_channels(city_name)


def schedule():
    sch = BlockingScheduler()
    sch.add_job(update_movies, 'cron', hour='01', id='update_movies')
    sch.add_job(match_channels_movie, 'cron', hour='01', minute='30', id='match_channels_movie')
    sch.add_job(update_prices, 'interval', minutes=5, id='update_prices')
    sch.add_job(match_channels_price, 'interval', minutes=17, id='match_channels_price')
    sch.add_job(update_cinema_min_price, 'interval', hours=1, id='update_cinema_min_price')
    sch.add_job(remove_expire_channels_price, 'cron', hour='0,5', minute='05', id='remove_expire_channels_price')
    sch.start()


def usage():
    print(
        """
Usage: python ops.py [option]
-h or --help：显示帮助信息
-s or --schedule: 系统自动调度更新
-m or --movie: 更新电影信息
--match-movie: 多渠道电影匹配
-c or --cinema：更新某个城市影院信息,例如： -c 上海
--match-cinema: 某个城市多渠道影院匹配,例如： --match-cinema 上海
-p or --price：更新某个城市价格信息,例如： -p 上海
--match-price：某个城市多渠道价格匹配,例如： --match-price 上海
"""
    )


if __name__ == '__main__':
    if len(sys.argv) == 1:
        usage()
        sys.exit()
    try:
        opts, args = getopt.getopt(sys.argv[1:], "hsmrc:p:",
                                   ["help", "schedule", "match-movie", "match-cinema=", "match-price=",
                                    "force-match-price="])  # sys.argv[1:] 过滤掉第一个参数
    except getopt.GetoptError:
        print("argv error,please input")

    for cmd, arg in opts:
        if cmd in ("-h", "--help"):
            usage()
            sys.exit()
        elif cmd in ("-s", "--schedule"):
            schedule()
        elif cmd in ("-m", "--movie"):
            update_movies()
        elif cmd in ("--match-movie",):
            match_channels_movie()
        elif cmd in ("-c", "--cinema"):
            update_cinemas(arg)
        elif cmd in ("--match-cinema",):
            match_cinemas(arg)
        elif cmd in ("-p", "--price"):
            update_city_prices(arg)
        elif cmd in ("--match-price",):
            match_city_channels_price(arg)
        elif cmd in ("--force-match-price",):
            force_match_city_channels_price(arg)
        elif cmd in ("-r", "--remove-expire",):
            remove_expire_channels_price()

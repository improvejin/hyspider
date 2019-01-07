import sys

import os

from apscheduler.schedulers.blocking import BlockingScheduler


sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from hyspider.manager.price import PriceManager

from wxpy import *

# 初始化机器人
bot = Bot()
# group_receiver = ensure_one(bot.groups().search('惠电影'))
me = bot.friends().search('Jin')[0]
logger = get_wechat_logger(bot.file_helper)

sch = BlockingScheduler()
price_manager = PriceManager.clone()


@sch.scheduled_job('cron', hour='6,7,8,9,10', id='notice_price_update_status')
def notice_price_update_status():
    msg = price_manager.get_price_update_status()
    logger.warning(msg)


@bot.register([me, bot.file_helper], TEXT,  except_self=False)
def get_price_update_status(msg):
    print(msg)
    if msg.text == 'h':
        logger.warning("""
h: show help
s: get status
c: crawlers status
rs: restart scrapyd
ro: restart ops.py
        """)
    elif msg.text == 's':
        notice_price_update_status()
    elif msg.text == 'c':
        from hyspider.settings import BOT_NAME, SCRAPYD_SERVER
        import requests
        import json
        params = {'project': BOT_NAME}
        rsp = requests.get(SCRAPYD_SERVER + '/listjobs.json', params)
        res = json.loads(rsp.text)
        running = res['running']
        pending = res['pending']
        s = '{} running, {}'.format(len(running), running)
        logger.warning(s)
        s = '{} pending, {}'.format(len(pending), pending)
        logger.warning(s)
    elif msg.text == 'rs':
        ret_code = restart_process('scrapyd')
        logger.warning(ret_code)


def restart_process(process_name):
    """根据进程名重启进程"""
    import psutil
    pid_list = psutil.pids()
    for pid in pid_list:
        try:
            each_pro = psutil.Process(pid)
            if process_name.lower() in each_pro.name().lower():
                each_pro.terminate()
                each_pro.wait(timeout=3)
        except psutil.NoSuchProcess:
            pass
    cmd = 'start scrapyd -d {}'.format(os.path.expanduser('~'))
    return os.system(cmd)


if __name__ == '__main__':
    sch.start()







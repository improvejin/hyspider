import logging

import requests

from hyspider.settings import IP_PROXY_SERVER

logging.getLogger("requests").setLevel(logging.WARNING)


def get_random_ip_port():
    r = requests.get(IP_PROXY_SERVER)
    return r.text

if __name__ == '__main__':
    print(get_random_ip_port())
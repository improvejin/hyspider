import random

from hyspider.utils.useragents import pc_user_agents


class UserAgentRandomMiddleware(object):

    @classmethod
    def from_crawler(cls, crawler):
        o = cls()
        return o

    def process_request(self, request, spider):
        agent = random.choice(pc_user_agents)
        request.headers.setdefault(b'User-Agent', agent)
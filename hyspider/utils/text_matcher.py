from aip import AipNlp
import time
from hyspider.utils.log import logger


class TextMatcher:
    APP_ID = '11351413'
    API_KEY = 'obeGkxkpn1c5ZPUL54MXGyeK'
    SECRET_KEY = '8NISO79cAvOWlwoXUoeirM48TPsPORGk'

    def __init__(self):
        self.client = AipNlp(self.APP_ID, self.API_KEY, self.SECRET_KEY)

    def sim(self, text1, text2):
        # 百度限制每秒查5次
        time.sleep(0.2)

        match_score = 0
        try:
            res = self.client.simnet(text1.replace('•', ''), text2.replace('•', ''))
            match_score = res['score']
        except UnicodeEncodeError:
            logger.error("UnicodeEncodeError: {}, {}", text1, text2)
        return match_score


if __name__ == '__main__':
    matcher = TextMatcher()
    res = matcher.sim("静安区南京西路1038号梅龙镇广场10楼（近江宁路）", "闵行区申长路688号虹桥天地购物中心6层(近舟虹路)")
    print(res['score'])
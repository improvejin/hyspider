import base64
import logging
import random
import sys
import os

import requests
from fontTools import ttLib

log = logging.getLogger(__name__)
base_font = ttLib.TTFont(os.path.expanduser('~') + '/base.woff')
base_unicode_list = base_font.getGlyphOrder()
base_unicode2num = {'x': '.', 'uniE541': '0', 'uniE820': '1', 'uniEBF1': '2', 'uniF5BE': '3', 'uniF0AE': '4',
                    'uniE406': '5', 'uniF74D': '6',
                    'uniF5F7': '7', 'uniE21D': '8', 'uniF4D9': '9'}


class MTFontParser:
    mt_unicode2num = dict()

    def __init__(self, woff):
        self.woff_file = self.get_woff_file(woff)
        mt_font = ttLib.TTFont(self.woff_file)
        mt_unicode_list = mt_font.getGlyphOrder()

        for mt_unicode in mt_unicode_list:
            mt_glyph = mt_font['glyf'][mt_unicode]
            for base_unicode in base_unicode_list:
                base_glyph = base_font['glyf'][base_unicode]
                if base_glyph == mt_glyph:
                    self.mt_unicode2num[mt_unicode] = base_unicode2num.get(base_unicode)
                    break

    def __del__(self):
        if os.path.exists(self.woff_file):
            os.remove(self.woff_file)

    def get_woff_file(self, woff):
        if woff.startswith('http'):
            r = requests.get(woff)
            code = r.content
        else:
            code = base64.b64decode(woff)

        woff_file = 'mt_font_{}.woff'.format(random.randint(0, sys.maxsize))
        with open(woff_file, 'wb') as f:
            f.write(code)

        return woff_file

    def parse_price(self, price_code):
        price_str = ''
        for c in price_code:
            if c != '.':
                i = hex(ord(c))
                key = 'uni' + str(i).lstrip('0x').upper()
                price_str += self.mt_unicode2num.get(key)
            else:
                price_str += '.'
        return price_str

    def parse_price2(self, price):
        numbers = price.strip(';').upper().replace('&#X', 'uni').split(';')
        s = str()
        for num in numbers:
            if num[0] == '.':
                s += '.'
                num = num[1:]
            n = self.mt_unicode2num.get(num)
            if n is not None:
                s += n
            else:
                log.error("no num found:" + num)

        return s


if __name__ == '__main__':
    home = os.path.expanduser('~')
    font = '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'
    parser = MTFontParser(font)
    price = parser.parse_price_ex('&#xea8a;&#xec3c;')
    print(price)





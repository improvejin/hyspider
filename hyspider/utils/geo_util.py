import json
from urllib import parse

import requests

from hyspider.items.base import LatLng, Point
from hyspider.utils.coordTransform_utils import gcj02_to_wgs84, wgs84_to_gcj02

geo_code_url = 'http://api.map.baidu.com/geocoder/v2/?output=json&ak=hHjBwKZxbdTcHE9LIpbu1Ww1zDG9B6L1&ret_coordtype=bd09ll&city={}&address={}'
geo_conv_url = 'http://api.map.baidu.com/geoconv/v1/?coords={},{}&from={}&to={}&ak=hHjBwKZxbdTcHE9LIpbu1Ww1zDG9B6L1'
geo_reverse_url = 'http://api.map.baidu.com/geocoder/v2/?location={}&output=json&pois=1&ak=hHjBwKZxbdTcHE9LIpbu1Ww1zDG9B6L1&coordtype=bd09ll'


def wgs2gcj(lng, lat):
    url = geo_conv_url.format(lng, lat, 1, 3)
    rsp = requests.get(url)
    lng_lat = json.loads(rsp.text)
    return lng_lat['result']


def wgs2bd(lng, lat):
    lng_lat = geo_conv_url.format(lng, lat, 1, 5)
    return lng_lat['result']


def gcj2bd(lng, lat):
    lng_lat = geo_conv_url.format(lng, lat, 3, 5)
    return lng_lat['result']


def get_district(addr, city=''):
    start = addr.find('市')
    if start == -1:
        start = 0
    else:
        start = start+1

    pos = addr.find('区')
    if pos == -1:
        print('no district info:', addr)
    elif start >0 and pos < start:
        # 类似这种金山区朱泾镇乐购超市一楼
        start = 0

    district = addr[start:pos+1].strip(city).lstrip('市')
    return district


def get_district_from_lat_lng(lat_lng):
    url = geo_reverse_url.format(lat_lng)
    rsp = requests.get(url)
    code = json.loads(rsp.text)
    if code['status'] == 0:
        return code['result']['addressComponent']['district'].replace('县', '区')  # 百度返回崇明县
    else:
        return ''


def parse_addr(city, addr):
    if addr[-1] == '）':  # 中文括号
        start = addr.rindex('（')
        addr = addr[0:start]
    if addr[-1] == ')':  # 中文括号
        start = addr.rindex('(')
        addr = addr[0:start]
    url = geo_code_url.format(parse.quote(city), parse.quote(addr))
    rsp = requests.get(url)
    code = json.loads(rsp.text)
    lat_lng = LatLng()
    if code['status'] == 0:
        result = code['result']
        location = result['location']
        lat_lng['lat_lng'] = '{},{}'.format(location['lat'], location['lng'])
        lat_lng['location'] = Point(location['lat'], location['lng'])
        lat_lng['precise'] = result['precise']
        lat_lng['confidence'] = result['confidence']
        return lat_lng
    else:
        print(addr)
        return None


if __name__ == '__main__':
    city = '合肥'
    addr = '合肥市胜利路与凤阳路交汇处(元一时代广场4楼C区)'
    district = get_district(addr, city)
    lat_lng = parse_addr(city, addr)['lat_lng']
    district = get_district_from_lat_lng(lat_lng)
    lng = float(lat_lng.split(',')[0])
    lat = float(lat_lng.split(',')[1])
    print(lng, lat)
    wgs = gcj02_to_wgs84(lng, lat)
    print(wgs)
    gcj = wgs84_to_gcj02(wgs[0], wgs[1])
    print(gcj)
    gcj1 = wgs2gcj(wgs[0], wgs[1])
    print(gcj1)
    wgs = gcj02_to_wgs84(gcj[0], gcj[1])
    print(wgs)
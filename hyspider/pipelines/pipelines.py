# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs

from scrapy.exceptions import DropItem


class ValidPipeline(object):
    def process_item(self, item, spider):
        if item['name'] == '全部':
            raise DropItem("ignore %s" % item)
        else:
            return item




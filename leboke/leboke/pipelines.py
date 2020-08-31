# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from leboke.items import LebokeItem
from leboke.items import LebokelessonItem
from leboke.items import LebokeSpeedItem
import json
import codecs


class LebokePipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://spider:spidermining@172.20.207.10:27051/spider_weidong?authSource=admin")
        self.db = self.client['spider_weidong']   #

    def process_item(self, item, spider):
        if isinstance(item, LebokelessonItem) and spider.name == 'leboke_xdf':
            table = self.db['leboke_lesson_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        elif isinstance(item, LebokeSpeedItem) and spider.name == 'leboke_speed':
            table = self.db['leboke_speed_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        else:
            table = self.db['leboke_class_detail']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo

        return item


    def close_spider(self, spider):
        self.client.close()

    # def __init__(self):
    #     self.filename = codecs.open('leboke_info.json', 'a+', encoding="utf-8")
    #
    #
    # def process_item(self, item, spider):
    #     if isinstance(item, LebokeItem):
    #         text = json.dumps(dict(item), ensure_ascii=False) + "\n"
    #         self.filename.write(text)
    #         return item
    #
    #
    # def close_spider(self, spider):
    #     self.filename.close()

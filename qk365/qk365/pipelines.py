# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json,codecs
import pymongo
from qk365.items import Qk365Item
from qk365.items import Qk365DealerItem
from qk365.items import Qk365CommunityItem

# class Qk365Pipeline:
#     def __init__(self):
#         self.filename = codecs.open('qke_info.json', 'a+', encoding="utf-8")
#
#
#     def process_item(self, item, spider):
#         text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#         self.filename.write(text)
#         return item
#
#
#     def close_spider(self, spider):
#         self.filename.close()


class Qk365Pipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://spider:spidermining@172.20.207.10:27051/spider_weidong?authSource=admin")
        self.db = self.client['spider_weidong']   #

    def process_item(self, item, spider):
        if isinstance(item, Qk365Item):
            table = self.db['qk365_hotel_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        if isinstance(item, Qk365DealerItem):
            table = self.db['qk365_dealer_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        if isinstance(item, Qk365CommunityItem):
            table = self.db['qk365_community_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        return item

    def close_spider(self, spider):
        self.client.close()
# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import redis
import time
import codecs
import pymongo
from yaodaoyun.items import YaodaoyunItem
from yaodaoyun.items import lessonItem

# class YaodaoyunPipeline:
#     def __init__(self):
#         self.filename = codecs.open('yaodaoyun_info.json', 'a+', encoding="utf-8")
#         self.filename1 = codecs.open('yaodaoyun_lesson_info.json', 'a+', encoding="utf-8")
#     # def open_spider(self, spider):
#     #     pass
#
#     def process_item(self, item, spider):
#         if isinstance(item, YaodaoyunItem):
#             text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#             self.filename.write(text)
#         if isinstance(item, lessonItem):
#             text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#             self.filename1.write(text)
#         return item
#
#     def close_spider(self, spider):
#         self.filename.close()
#         self.filename1.close()

class YaodaoyunPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://spider:spidermining@172.20.207.10:27051/spider_weidong?authSource=admin")
        self.db = self.client['spider_weidong']   #

    def process_item(self, item, spider):
        if isinstance(item, YaodaoyunItem):
            table = self.db['wangyiyun_class_detail']
            detail_info = dict(item)  # item转换为字典格式
            
            table.insert(detail_info)  # 将item写入mongo

        if isinstance(item, lessonItem):
            table = self.db['wangyiyun_lesson_detail']
            detail_info = dict(item)  # item转换为字典格式

            table.insert(detail_info)  # 将item写入mongo
        #spider.logger.info('------结束时间：{}---------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        return item


    def close_spider(self, spider):
        spider.logger.info('------结束时间：{}---------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self.client.close()

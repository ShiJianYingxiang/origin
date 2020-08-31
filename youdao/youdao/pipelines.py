# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
from youdao.items import YoudaoItem
from youdao.items import Youdaoteacher_Item
import pymongo


# class YoudaoPipeline:
#     def __init__(self):
#         pass
#
#
#     def process_item(self, item, spider):
#         # if spider.name == 'youdao_class_info' :
#         if isinstance(item, YoudaoItem) and spider.name == 'youdao_class_info':
#             file_path = 'youdao_class_info.json'
#             # filename = codecs.open(file_path, 'a+', encoding="utf-8")
#             # text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#             # filename.write(text)
#             with open(file_path, 'a+', encoding="utf-8") as f:
#                 text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#                 f.write(text)
#
#         elif spider.name == 'youdao_lesson_info':
#             file_path1 = 'youdao_lesson_info.json'
#             # filename = codecs.open(file_path1, 'a+', encoding="utf-8")
#             # text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#             # filename.write(text)
#             with open(file_path1, 'a+', encoding="utf-8") as f:
#                 text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#                 f.write(text)
#         return item
#
#
#     def close_spider(self, spider):
#         pass
#         # self.filename.close()
#
#
# class YoudaoteacherPipeline:
#     def __init__(self):
#         self.filename = codecs.open('youdaoteacher_info.json', 'a+', encoding="utf-8")
#
#
#     def process_item(self, item, spider):
#         if isinstance(item, Youdaoteacher_Item):
#             text = json.dumps(dict(item), ensure_ascii=False) + "\n"
#             self.filename.write(text)
#             return item
#
#
#     def close_spider(self, spider):
#         self.filename.close()

# ================================================
class YoudaoPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://spider:spidermining@172.20.207.10:27051/spider_weidong?authSource=admin")
        self.db = self.client['spider_weidong']   #

    def process_item(self, item, spider):
        # if spider.name == 'youdao_class_info' :
        if isinstance(item, YoudaoItem) and spider.name == 'youdao_class_info':
            table = self.db['youdao_class_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo

        elif spider.name == 'youdao_lesson_info':
            table = self.db['youdao_lessons_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
        return item

    def close_spider(self, spider):
        self.client.close()


class YoudaoteacherPipeline:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://spider:spidermining@172.20.207.10:27051/spider_weidong?authSource=admin")
        self.db = self.client['spider_weidong']   #

    def process_item(self, item, spider):
        if isinstance(item, Youdaoteacher_Item):
            table = self.db['youdao_teacher_info']
            detail_info = dict(item)  # item转换为字典格式
            table.insert(detail_info)  # 将item写入mongo
            return item


    def close_spider(self, spider):
        self.client.close()



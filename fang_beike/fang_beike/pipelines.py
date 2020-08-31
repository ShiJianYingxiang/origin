# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, codecs, time,redis
from fang_beike.items import FangBeikeItem,FangBeikeErShouViewerItem
try:
    # url_db = redis.StrictRedis(host='112.126.102.89', port=6379, db=7, password='dalian')
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None



class FangBeikePipeline(object):
    def __init__(self):
        self.filename = codecs.open('/mnt/data/weidong.shi/file/beike/new_house_rank/' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding="utf-8")
        self.filename1 = codecs.open('/mnt/data/weidong.shi/file/beike/ershou_viewer_info/' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding="utf-8")
        # self.filename = codecs.open('room_info.json', 'a+', encoding="utf-8")
        # self.filename1 = codecs.open('ershou_info.json', 'a+', encoding="utf-8")


    def process_item(self, item, spider):
        if isinstance(item, FangBeikeItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.filename.write(text)


        if isinstance(item, FangBeikeErShouViewerItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.filename1.write(text)
            spider.url_db.sadd('ke_citys:ershou_successful_set', item['room_id'])
        return item


    def close_spider(self, spider):
        spider.logger.info('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self.filename.close()
        self.filename1.close()

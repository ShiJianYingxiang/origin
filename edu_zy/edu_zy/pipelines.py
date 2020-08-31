# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json, codecs, time, redis
from edu_zy.items import EduZyItem, EduZyCourseBatchItem
try:
    # url_db = redis.StrictRedis(host='112.126.102.89', port=6379, db=7, password='dalian')
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None


class EduZyPipeline(object):
    def __init__(self):
        self.filename = codecs.open('/mnt/data/weidong.shi/file/education_zhuoyue_class/' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding="utf-8")
        #self.filename1 = codecs.open('/mnt/data/weidong.shi/file/edu_zhuoyue_course_detail/' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding="utf-8")
        # self.filename = codecs.open('course_detail_info.json', 'a+', encoding="utf-8")
        # self.filename1 = codecs.open('course_list_info.json', 'a+', encoding="utf-8")



    def process_item(self, item, spider):
        if isinstance(item, EduZyItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            spider.url_db.rpush('edu_zhuoyue:detail_successful_list', 'None')
            self.filename.write(text)
        return item

        #if isinstance(item, EduZyCourseBatchItem):
        #    text = json.dumps(dict(item), ensure_ascii=False) + "\n"
        #    self.filename1.write(text)
        #    spider.url_db.rpush('edu_zhuoyue:course_successful_list', 'None')
        #return item


    def close_spider(self, spider):
        # spider.logger.info('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        self.filename.close()
        #self.filename1.close()

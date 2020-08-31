# -*- coding: utf-8 -*-
import scrapy
import redis
import re
import requests
import json
import time
from youdao.items import YoudaoItem

class YoudaoLessonInfoSpider(scrapy.Spider):
    name = 'youdao_lesson_info'
    allowed_domains = ['youdao.com']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    try:
        redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        redis_db = None
    base_key = 'swd_youdao'
    detail_id_set_key = "{}:detail_id_set".format(base_key)
    off_id_set_key = "{}:off_id_set".format(base_key)


    def start_requests(self):
        '''
        将redis中list的数据rpoplpush
        针对lpop:
        每次弹出10个
        列表中数据量小时，这种方法还行
        如果列表中数据量大时，？？？？
        '''
        for _ in range(self.redis_db.scard(self.detail_id_set_key)):
            detail_id = self.redis_db.spop(self.detail_id_set_key)
            detail_id = detail_id.decode('utf-8')
        # detail_ids = ['58136', '58639', '54750']
        # for detail_id in detail_ids:
            lesson_url = 'https://ke.youdao.com/course/api/detail.json?courseId=%s'%detail_id
            yield scrapy.Request(url=lesson_url, meta={'detail_id': detail_id}, callback=self.parse)


    def parse(self, response):
        detail_id = response.meta.get('detail_id', '')
        data = json.loads(response.text)

        try:
            course_infos = data.get('course', '').get('lessonList', [])[0].get('list', [])
            item = YoudaoItem()
            for course_temp in course_infos:
                if 'list' not in course_temp.keys():
                    for course_key, course_value in course_temp.items():
                        item[course_key] = course_value
                        item['product_id'] = detail_id
                        item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    yield item
                else:
                    course_temp_list = course_temp.get('list', [])
                    if course_temp_list:
                        for course_temp_content in course_temp_list:
                            for course_key, course_value in course_temp_content.items():
                                item[course_key] = course_value
                                item['product_id'] = detail_id
                                item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                            yield item
        except:
            self.redis_db.sadd(self.off_id_set_key, detail_id)












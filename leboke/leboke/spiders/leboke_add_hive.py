# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import time
import logging
import redis
from leboke.items import LebokeItem
from leboke.items import LebokelessonItem
from pyhive import hive

class LebokeXdfSpider(scrapy.Spider):
    name = 'leboke_xdf_add111'
    # allowed_domains = ['xdf.cn']
    # start_urls = ['https://dfubapi.xdf.cn/system/listquarter.json']
    headers = {
                "User-Agent": "LBOC_Student/5.6.3 iPhone11,6; iOS 13.3.1; Scale/3.00)",
                "X-Device-Id": "F2B14E79-0598-4FAA-AF97-DB518EF49733",
    }
    headers1 = {
        "User-Agent": "LBOC_Student/5.6.3 iPhone11,6; iOS 13.3.1; Scale/3.00)",
        "X-Device-Id": "F2B14E79-0598-4FAA-AF97-DB518EF49733",
        "Content-Type": "application/json",
        "referer": "none",
    }
    item = LebokeItem()

    hive_host = '172.20.207.6'
    hive_port = 10000
    hive_username = 'supdev'
    hive_database = 'default'

    lesson_url = 'https://dfub.xdf.cn/class/outline.json'
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None


    def start_requests(self):
        self.logger.info('------Start_requests_End_time:{}-----------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        conn = hive.Connection(host=self.hive_host, port=self.hive_port, username=self.hive_username, database=self.hive_database)
        cursor = conn.cursor()
        sql = "SELECT t.classcode FROM (SELECT t.classcode, max(t.lessoncount) lessoncount FROM ods.spider_education_leboke_v2_class_detail t GROUP BY t.classcode) t LEFT JOIN (SELECT count(NO) c, classcode FROM ( SELECT classcode, NO FROM ods.spider_education_leboke_v2_lesson_detail t WHERE dt >= '2020-07-21' GROUP BY classcode, NO) t GROUP BY classcode) t1 ON t.classcode = t1.classcode WHERE cast(lessoncount AS bigint) > nvl(c,0)"
        cursor.execute(sql)
        for result in cursor.fetchall():
            classcode = result[0]
            lesson_data = {
                'code': classcode
            }
            # 课程详情解析
            yield scrapy.Request(url=self.lesson_url, headers=self.headers1, method='post', meta={'classCode': classcode},
                                 body=json.dumps(lesson_data), callback=self.parse)


    #
    def parse(self, response):
        '''
        '''
        classCode = response.meta.get('classCode', '')
        data = json.loads(response.text)
        lessonitem = LebokelessonItem()
        data_list = data.get('data', [])
        if not data_list:
            lessonitem['classCode'] = classCode
            lessonitem['crawl_flag'] = 0  # crawl_flag为0 代表抓取过这个课程
            lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem

        for data_temp in data_list:
            for temp_key, temp_value in data_temp.items():
                lessonitem['classCode'] = classCode
                lessonitem[temp_key] = temp_value
                lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem

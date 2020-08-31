# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import time
import logging
import redis
from leboke.items import LebokeItem
from leboke.items import LebokelessonItem

class LebokeXdfSpider(scrapy.Spider):
    name = 'leboke_xdf_add'
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
    lesson_url = 'https://dfub.xdf.cn/class/outline.json'
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None


    def start_requests(self):
        self.logger.info('------Start_requests_End_time:{}-----------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        while 1:
            body = self.url_db.rpop('leboke_list')
            if body:
                if isinstance(body, bytes):
                    body = body.decode()
                    # 获取classcode
                    # 1AK203C1SX02 ,1AK203C1SX03, 1AK203C1SX07,1AK203C1SX08,1AK203C1SX09
                    print(body, '=========', type(body))
                    classcode = body
                    lesson_data = {
                        'code': classcode
                    }
                    # 课程详情解析
                    yield scrapy.Request(url=self.lesson_url, headers=self.headers1, method='post', meta={'classCode': classcode},
                                         body=json.dumps(lesson_data), callback=self.parse)
            else:
                break
                self.logger.info('该队列已经跑完了')


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

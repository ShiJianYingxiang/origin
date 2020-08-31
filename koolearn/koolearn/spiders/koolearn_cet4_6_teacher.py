# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import datetime
import time
import copy
import re
from koolearn.items import KoolearnItem
from lxml import etree

class KoolearnCet46Spider(scrapy.Spider):
    name = 'koolearn_cet4_6_teacher'
    headers = {
        'Referer': 'https://cet4.koolearn.com/zhuanti/cet/?from=shouye_ce4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    def start_requests(self):
        request_url = 'https://item.koolearn.com/product-search/api/product/?callback=jQuery111209925576659011579_1589964831724&productIds=57962%2C57963%2C40657%2C40658%2C49324%2C49326%2C58673%2C59319%2C57012%2C57756%2C58321%2C54479%2C51480%2C55035%2C53250%2C50509%2C51159%2C48447%2C45168%2C50177%2C48212%2C43141'
        yield scrapy.Request(url=request_url, headers= self.headers, callback=self.parse)



    def parse(self, response):
        '''
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        '''
        data = response.text
        datas = re.search(r'\(.*?\)', data).group()
        data = json.loads(datas.replace('(', '').replace(')', ''))
        class_list = data.get('data', [])

        item = KoolearnItem()
        # teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        for class_info in class_list:
            teacher_class_id = class_info.get('productId', '')
            teacher_infos_list = class_info.get('teachers', [])
            for teacher_info in teacher_infos_list:
                teacher_name = teacher_info.get('teacherName', '')     #a.teacher_name
                teacher_id = teacher_info.get('teacherId', '')         #a.teacher_id

                item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                item['class_id'] = teacher_class_id
                item['teacher_id'] = teacher_id
                item['teacher_name'] = teacher_name
                yield item

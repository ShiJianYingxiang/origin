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
    name = 'koolearn_cet4_6'
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
        class_list = data.get('data', '')

        item = KoolearnItem()
        # teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        class_time = chapter_id = chapter = arrangement_type = arrangement = teacher_tag = teacher_type = teacher_phone = subject_id = subject = class_type_id = class_type = ''
        for class_info in class_list:
            class_name = class_info.get('name', '')   #class_name
            class_id = class_info.get('productId', '')   #
            register_count = class_info.get('buyNumber', '')  #
            max_count = class_info.get('stock', '')  #
            lesson_count = class_info.get('classHours', '')  #
            grade_name = class_info.get('productLineName', '')  #
            stage_name = grade_name
            grade_id = class_info.get('productLine', '')  #
            stage_id = grade_id

            teacher_infos_list = class_info.get('teachers', [])
            for teacher_info in teacher_infos_list:
                teacher_name = teacher_info.get('teacherName', '')     #a.teacher_name
                teacher_id = teacher_info.get('teacherId', '')         #a.teacher_id
                item['teacher_name'] = teacher_name
                item['teacher_id'] = teacher_id

            detail_url = 'https://www.koolearn.com/product/c_{0}_{1}.html'.format(grade_id, class_id)


            item['class_name'] = class_name
            item['class_id'] = class_id
            item['class_type'] = class_name
            item['class_type_id'] = class_type_id
            item['subject'] = subject
            item['subject_id'] = subject_id
            item['register_count'] = register_count
            item['max_count'] = max_count
            item['teacher_phone'] = teacher_phone
            item['teacher_type'] = teacher_type
            item['teacher_tag'] = teacher_tag
            item['arrangement'] = arrangement
            item['arrangement_type'] = arrangement_type
            item['lesson_count'] = lesson_count
            item['chapter'] = chapter
            item['chapter_id'] = chapter_id
            item['grade_name'] = grade_name
            item['grade_id'] = grade_id
            item['stage_name'] = stage_name
            item['stage_id'] = stage_id
            item['class_time'] = class_time
            item['detail_url'] = detail_url
            yield scrapy.Request(url=detail_url, meta={'item': copy.deepcopy(item)}, callback = self.otherinfo_parse)


    def otherinfo_parse(self, response):
        price = response.xpath('''//span[@class="jg-control-price"]/text()|//span[@class="p-price"]//span/text()''').get()

        origin_price = response.xpath('''//span[@class="p-line-through"]/text()''').get()
        if origin_price:
            origin_price = origin_price.replace('¥', '')

        end_date_str = response.xpath('''(//div[@class="p-product-info"]//p)[1]//a''').get()
        end_date_str = re.search(r'\s*(\d{4}-\d+-\d+)\s*', end_date_str).group(1)
        end_date = str(datetime.datetime.strptime(end_date_str, '%Y-%m-%d'))

        # item = KoolearnItem()

        time_flag = response.xpath('''(//div[@class="p-product-info"]//p)[1]/text()''').get().strip()
        if '开课时间' in time_flag:
            start_time_str = re.search(r'开课时间\s*[:：]\s*(\d{4}-\d+-\d+)\s*课时', time_flag).group(1)
            start_date = datetime.datetime.strptime(start_time_str, '%Y-%m-%d')
            start_date = str(start_date)
        else:
            start_time = response.xpath('''(//ul[@id="jp-live-outline"]//li//div//span[@class="date"])[1]''').get()
            if start_time:
                start_date = re.search('\d{4}-\d+-\d+ \d+:\d+', start_time).group(0)
            else:
                start_date = ''
        item = response.meta['item']
        item['price'] = price
        item['origin_price'] = origin_price
        item['start_date'] = start_date
        item['end_date'] = end_date
        yield item



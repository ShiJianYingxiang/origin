# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import datetime
import time
from koolearn.items import KoolearnItem

class KoolearnSpiderSpider(scrapy.Spider):
    name = 'koolearn_spider'
    allowed_domains = ['koolearn.com']
    # start_urls = ['http://koolearn.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    def start_requests(self):
        for i in range(1, 13):
            base_url = 'https://item.kooup.com/product/course-center?grade={}&seasonName=2020%E6%9A%91%E5%81%87'.format(str(i))
            response = requests.get(base_url, headers = self.headers)
            datas = json.loads(response.text)
            totalpage = datas.get('data', '').get('totalPage', '')
            for temp in range(1, totalpage+1):
                request_url = base_url + '&pageNo=' + str(temp)
                yield scrapy.Request(url=request_url, callback=self.parse)
    #
        # request_url = 'https://item.kooup.com/product/course-center?grade=1&subject=-1&seasonName=2020%E6%9A%91%E5%81%87&stage=-1&classType=-1&pageNo=1'
        # yield scrapy.Request(url=request_url, callback=self.parse)


    def parse(self, response):
        '''
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        '''
        data = json.loads(response.text)
        class_list = data.get('data', '').get('list', [])
        item = KoolearnItem()
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        for class_info in class_list:
            grade_name = class_info.get('grade', '').get('name', '')   #年级名称    a.grade_name
            grade_id = class_info.get('grade', '').get('id', '')      #年级名称对应的数   a.grade_id
            if grade_id <= 6:
                stage_name = '小学'
            elif 6 < grade_id <= 9:
                stage_name = '初中'
            else:
                stage_name = '高中'
            subject = class_info.get('subject', '').get('name', '')    #subject
            subject_id = class_info.get('subject', '').get('id', '')    #subject_id
            arrangement_type = class_info.get('basicCourseType', '').get('name', '')  # arrangement_type

            teacher_class_id = class_info.get('singleProductId', '')   #给老师用的课程ID
            teacher_infos = class_info.get('teachers', [])
            for teacher_info in teacher_infos:
                teacher_name = teacher_info.get('name', '')     #a.teacher_name
                teacher_id = teacher_info.get('teacherId', '')  #a.teacher_id
                teacher_type = teacher_info.get('typeName', '')  # a.teacher_type
                                                                #a.teacher_phone
                                                                #a.teacher_tag
                item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                item['class_id'] = teacher_class_id
                item['teacher_id'] = teacher_id
                item['teacher_name'] = teacher_name
                yield item

            products_infos = class_info.get('products', [])
            for products_info in products_infos:
                class_name = products_info.get('productName', '')    #课程名称---a.class_name|a.class_type
                class_id = products_info.get('productId', '')    #课程ID---a.class_id
                class_type_id = ''
                price = products_info.get('price', '')          #课程价格---price
                origin_price = products_info.get('promotionPrice', '')  #促销价格---origin_price
                liveTimeDesc = products_info.get('liveTimeDesc', '')  #直播时间
                liveDateDesc = products_info.get('liveDateDesc', '')    #直播的时间间隔(开始时间---结束时间)
                if '月' in liveDateDesc and '日' in liveDateDesc:
                    liveTimeDesc = liveTimeDesc.split('-')
                    liveDateDesc = liveDateDesc.split('-')
                    year = datetime.datetime.now().year
                    start_time = (liveDateDesc[0] + ' ' + liveTimeDesc[0]).replace('月', '-').replace('日', '')
                    end_time = (liveDateDesc[1] + ' ' + liveTimeDesc[1]).replace('月', '-').replace('日', '')
                    start_time = str(year) + '-' + start_time
                    end_time = str(year) + '-' + end_time
                    start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
                    end_date = datetime.datetime.strptime(end_time, '%Y-%m-%d %H:%M')
                    end_date = str(end_date)
                    start_date = str(start_date)
                else:
                    start_date = ''
                    end_date = ''
                lesson_count = products_info.get('liveCount', '')        #课时数--a.lesson_count
                detail_url = products_info.get('productUrl', '').replace('?subClassId=-1', '')        #详情页url ---a.detail_url
                if 'https:' not in detail_url:
                    detail_url = 'https:' + detail_url
                max_count = products_info.get('productStock', '')      #a.max_count
                register_count = products_info.get('buyNumber', '')    #a.register_count

                item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                item['class_name'] = class_name
                item['class_id'] = class_id
                item['class_type'] = class_name
                item['class_type_id'] = class_type_id
                item['subject'] = subject
                item['subject_id'] = subject_id
                item['price'] = price
                item['origin_price'] = origin_price
                item['register_count'] = register_count
                item['max_count'] = max_count
                item['start_date'] = start_date
                item['end_date'] = end_date
                item['teacher_name'] = teacher_name
                item['teacher_id'] = teacher_id
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
                yield item
#


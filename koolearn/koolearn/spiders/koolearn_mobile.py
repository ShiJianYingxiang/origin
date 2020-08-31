# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import datetime
import time
import re
from koolearn.items import KoolearnItem#,Koolearn_teacherinfo_Item
#
class KoolearnMobileSpider(scrapy.Spider):
    name = 'koolearn_mobile'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }


    def start_requests(self):
        year1 = datetime.datetime.now().year
        format_url = 'https://item.kooup.com/product/course-center?grade={}&subject=-1&seasonName={}'
        grade_list = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
        term_list = ['暑假', '秋季']
        for grade_item in grade_list:
            for term_item in term_list:
                base_url =format_url.format(grade_item, str(year1)+term_item)
                yield scrapy.Request(url=base_url, headers=self.headers, meta={'grade': grade_item, 'term': term_item}, callback=self.get_page_nums)
        # base_url = 'https://item.kooup.com/product/course-center?&pageNo=1&subject=-1&seasonName={}%E6%9A%91%E5%81%87'.format(str(year1))
        # base_url = 'https://item.kooup.com/product/course-center?&pageNo=1&subject=-1&seasonName={}%E7%A7%8B%E5%AD%A3'.format(str(year1))

    def get_page_nums(self, response):
        grade = response.meta.get('grade', '')
        term = response.meta.get('term', '')
        datas = json.loads(response.text)
        totalpage = datas.get('data', '').get('totalPage', '')
        self.logger.info('--{}年级的{}总共有{}页-------'.format(grade, term, totalpage))
        for temp in range(1, totalpage+1):
            request_url = response.url + '&pageNo={}'.format(str(temp))
            yield scrapy.Request(url=request_url, headers=self.headers, callback=self.parse)


    def parse(self, response):
        data = json.loads(response.text)
        class_list = data.get('data', '').get('list', [])
        item = KoolearnItem()
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        for class_info in class_list:
            grade_name = class_info.get('grade', '').get('name', '')  # 年级名称    a.grade_name
            grade_id = class_info.get('grade', '').get('id', '')  # 年级名称对应的数   a.grade_id
            if grade_id <= 6:
                stage_name = '小学'
            elif 6 < grade_id <= 9:
                stage_name = '初中'
            else:
                stage_name = '高中'

            subject = class_info.get('subject', '').get('name', '')  # subject
            subject_id = class_info.get('subject', '').get('id', '')  # subject_id
            arrangement_type = class_info.get('basicCourseType', '').get('name', '')  # arrangement_type

            # teacher_class_id = class_info.get('singleProductId', '')   #给老师用的课程ID

            teacher_infos = class_info.get('teachers', [])
            for teacher_info in teacher_infos:
                teacher_name = teacher_info.get('name', '')  # a.teacher_name
                teacher_id = teacher_info.get('teacherId', '')  # a.teacher_id
                teacher_type = teacher_info.get('typeName', '')  # a.teacher_type


            products_infos = class_info.get('products', [])
            for products_info in products_infos:
                subClassId = products_info.get('subClassId', '')
                class_name = products_info.get('productName', '')  # 课程名称---a.class_name|a.class_type
                class_id = products_info.get('productId', '')  # 课程ID---a.class_id
                class_type_id = ''
                price = products_info.get('price', '')  # 课程价格---price
                origin_price = products_info.get('promotionPrice', '')  # 促销价格---origin_price


                liveTimestart_end = products_info.get('liveTimeAndBreakSlogan', '')  # 直播时间(开始和结束标志)
                time_start_end = re.search('\d+月\d+日-\d+月\d+日 \d+:\d+-\d+:\d+', liveTimestart_end).group()
                time_month = time_start_end.split(' ')[0]
                time_hours = time_start_end.split(' ')[1]
                time_hours_split = time_hours.split('-')
                time_month_split = time_month.split('-')
                year = datetime.datetime.now().year
                start_time = (time_month_split[0] + ' ' + time_hours_split[0]).replace('月', '-').replace('日', '')
                end_time = (time_month_split[1] + ' ' + time_hours_split[1]).replace('月', '-').replace('日', '')
                start_time = str(year) + '-' + start_time
                end_time0 = str(year) + '-' + end_time
                start_date = datetime.datetime.strptime(start_time, '%Y-%m-%d %H:%M')
                end_date = datetime.datetime.strptime(end_time0, '%Y-%m-%d %H:%M')
                if start_date > end_date:
                    end_time1 = str(year + 1) + '-' + end_time
                    end_date = datetime.datetime.strptime(end_time1, '%Y-%m-%d %H:%M')
                end_date = str(end_date)
                start_date = str(start_date)

                lesson_count = products_info.get('liveCount', '')  # 课时数--a.lesson_count
                detail_url = products_info.get('productUrl', '')  # 详情页url ---a.detail_url
                if 'https:' not in detail_url:
                    detail_url = 'https:' + detail_url
                max_count = products_info.get('productStock', '')  # a.max_count
                register_count = products_info.get('buyNumber', '')  # a.register_count


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
                item['subClassId'] = subClassId
                yield item

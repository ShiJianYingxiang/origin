# -*- coding: utf-8 -*-
import scrapy
import codecs
import requests
import json
import datetime
import time
from koolearn.items import KoolearnItem

class KoolearnMobileLessonSpider(scrapy.Spider):
    name = 'koolearn_mobile_lesson'
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
        for class_info in class_list:
            product_id = class_info.get('singleProductId', '')   #产品ID
            lesson_url = 'https://item.kooup.com/product/outline/%s'% product_id
            yield scrapy.Request(url=lesson_url, meta={'product_id': product_id}, callback=self.lesson_info)

    def lesson_info(self, response):

        data = json.loads(response.text)
        product_id = response.meta.get('product_id')
        lesson_info_lists = data.get('data', '').get('outline', [])
        lesson_infos = {'product_id': product_id, 'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')}

        file_name = '/mnt/data/weidong.shi/file/kooup_phone_lesson/' + time.strftime('%Y-%m-%d') + '.json'

        for lesson_info in lesson_info_lists:
            lessonTimes = lesson_info.get('lessonTimes', [])
            for temp in lessonTimes:
                lesson_infos.update(temp)
                with codecs.open(file_name, 'a+', encoding="utf-8") as xx:
                    text = json.dumps(dict(lesson_infos), ensure_ascii=False) + '\n'
                    xx.write(text)

           # item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
           # item['lesson'] = lesson_infos
           # yield item














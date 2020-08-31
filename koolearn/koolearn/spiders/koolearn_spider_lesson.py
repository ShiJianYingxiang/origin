# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import datetime
import time
import codecs
from koolearn.items import KoolearnItem

class KoolearnSpiderLessonPySpider(scrapy.Spider):
    name = 'koolearn_spider_lesson'
    # allowed_domains = ['koolearn.com']
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

    def parse(self, response):
        '''
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        '''
        data = json.loads(response.text)
        class_list = data.get('data', '').get('list', [])

        for class_info in class_list:
            product_id = class_info.get('singleProductId', '')   #给老师用的课程ID
            lesson_url = 'https://item.kooup.com/product/outline/%s'%product_id
            yield scrapy.Request(url=lesson_url, meta={'product_id': product_id}, callback=self.lesson_info)


    def lesson_info(self, response):

        data = json.loads(response.text)
        product_id = response.meta.get('product_id')
        lesson_info_lists = data.get('data', '').get('outline', [])
        lesson_infos = {'product_id': product_id, 'crawl_time': time.strftime('%Y-%m-%d %H:%M:%S')}

        item = KoolearnItem()
        file_name = time.strftime('%Y-%m-%d') + '.json'

        for lesson_info in lesson_info_lists:
            lessonTimes = lesson_info.get('lessonTimes', [])
            for temp in lessonTimes:
                lesson_infos.update(temp)

            xx = codecs.open(file_name, 'a+', encoding="utf-8")
            text = json.dumps(dict(lesson_infos), ensure_ascii=False) + '\n'
            xx.write(text)
        xx.close()
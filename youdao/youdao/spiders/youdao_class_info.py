# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import time
import re
import redis
import logging
from youdao.items import YoudaoItem
from youdao.items import Youdaoteacher_Item

class YoudaoClassInfoSpider(scrapy.Spider):
    name = 'youdao_class_info'
    item = YoudaoItem()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    try:
        redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        redis_db = None
    base_key = 'swd_youdao'
    detail_id_set_key = "{}:detail_id_set".format(base_key)
    tag_id_set_key = "{}:tag_id_set".format(base_key)
    tag_set = set()

    def start_requests(self):
        tag_url = 'https://ke.youdao.com/course3/api/content/stages'
        response = requests.get(tag_url, headers=self.headers, verify=False)
        tag_ids = re.findall('tagId\s*[\'\"]\s*:\s*(\d+)\,', response.text)
        for temp_id in tag_ids:
            self.tag_set.add(temp_id)   #125
        #     -----------------------
        tag_new_url = 'https://ke.youdao.com/course3/api/webhome'
        new_response = requests.get(tag_new_url, headers=self.headers)
        datas = json.loads(new_response.text)
        fixed_tag_list = datas.get('data', '').get('fixedEntries', [])

        lists = ['2012', '2632', '2056', '572']
        for item in lists:
            self.tag_set.add(item)

        for temp in fixed_tag_list:
            ptag_id = temp.get('tag', '').get('id', '')
            self.tag_set.add(ptag_id)
            subTag_list = temp.get('tag', '').get('subTag', [])
            for sub_temp in subTag_list:
                sub_tag = sub_temp.get('id', '')
                self.tag_set.add(sub_tag)

        for tag_id in self.tag_set:
            self.redis_db.sadd(self.tag_id_set_key, tag_id)
            tag_first_url = 'https://ke.youdao.com/course3/api/vertical2?tag=%s'% tag_id
            yield scrapy.Request(url=tag_first_url, callback=self.parse)


    def parse(self, response):
        '''
        第一次是解析courses
        '''
        tag_id = re.search('tag=(\d+)', response.url).group(1)
        data = json.loads(response.text)
        courses_list = data.get('data', '').get('courses', [])
        teacher_item = Youdaoteacher_Item()

        for temp in courses_list:
            detail_id = temp.get('id', '')   #详情页ID用来去重
            rank = temp.get('rank', '')      #rank用来翻页
            self.redis_db.sadd(self.detail_id_set_key, detail_id)
            for temp_key, temp_value in temp.items():
                self.item['tag_id'] = tag_id
                self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.item[temp_key] = temp_value
            yield self.item
            # -------------parse:teacher_info-----------------------
            teacher_list = temp.get('teacherList', [])
            for teacher_info in teacher_list:
                for teacher_key, teacher_value in teacher_info.items():
                    teacher_item[teacher_key] = teacher_value
                    teacher_item['tag_id'] = tag_id
                    teacher_item['product_id'] = detail_id
                    teacher_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                yield teacher_item

        if rank != 0:
            next_page_url = 'https://ke.youdao.com/course3/api/content/course?tag={0}&rank={1}'.format(tag_id, rank)
        yield scrapy.Request(url=next_page_url, callback=self.parse_detail)   #传递采集到的item meta={'item':item,'tag_id':tag_id},


    def parse_detail(self,response):
        tag_id = re.search('tag=(\d+)', response.url).group(1)
        data = json.loads(response.text)
        courses_list = data.get('data', '').get('course', [])
        teacher_item = Youdaoteacher_Item()
        if courses_list:
            for temp in courses_list:
                detail_id = temp.get('id', '')  # 详情页ID用来去重
                rank = temp.get('rank', '')  # rank用来翻页
                self.redis_db.sadd(self.detail_id_set_key, detail_id)
                for temp_key, temp_value in temp.items():
                    self.item['tag_id'] = tag_id
                    self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.item[temp_key] = temp_value
                yield self.item
                # -------------parse:teacher_info-----------------------
                teacher_list = temp.get('teacherList', [])
                for teacher_info in teacher_list:
                    for teacher_key, teacher_value in teacher_info.items():
                        teacher_item[teacher_key] = teacher_value
                        teacher_item['tag_id'] = tag_id
                        teacher_item['product_id'] = detail_id
                        teacher_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    yield teacher_item
            if rank != 0:
                next_page_url = 'https://ke.youdao.com/course3/api/content/course?tag={0}&rank={1}'.format(tag_id, rank)
            yield scrapy.Request(url=next_page_url, callback=self.parse_detail)




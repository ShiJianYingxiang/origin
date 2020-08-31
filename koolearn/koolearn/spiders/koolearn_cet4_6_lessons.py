# -*- coding: utf-8 -*-
import scrapy
import time
import copy
import requests
import json
import re
from scrapy.spiders import Spider
import logging

from koolearn.items import KoolearnItem

class KoolearnCet46LessonsPySpider(scrapy.Spider):
    name = 'koolearn_cet4_6_lessons'
    headers = {
        'Referer': 'https://cet4.koolearn.com/zhuanti/cet/?from=shouye_ce4',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }

    def start_requests(self):
        request_url = 'https://item.koolearn.com/product-search/api/product/?&productIds=57962%2C57963%2C40657%2C40658%2C49324%2C49326%2C58673%2C59319%2C57012%2C57756%2C58321%2C54479%2C51480%2C55035%2C53250%2C50509%2C51159%2C48447%2C45168%2C50177%2C48212%2C43141'
        yield scrapy.Request(url=request_url, headers= self.headers, callback=self.parse)


    def parse(self, response):
        '''
        teacher_phone = teacher_tag = arrangement = chapter = chapter_id = stage_id = class_time = ''
        '''
        data = json.loads(response.text)
        class_list = data.get('data', '')
        item = KoolearnItem()
        for class_info in class_list:
            class_id = class_info.get('productId', '')  #
            item['class_id'] = class_id
            get_pathid_url = 'https://study.koolearn.com/tongyong/baseLessonOfProductInfo/%s' % str(class_id)  #获取pathid
            pathid_response = requests.get(url=get_pathid_url, headers=self.headers, verify=False)
            pathid_infos = json.loads(pathid_response.text)
            pathid_list = pathid_infos.get('data', '').get('lessonStage', [])
            for pathid_info in pathid_list:
                pathid = pathid_info.get('id', '')
                if pathid:
                    get_nodeid_url = 'https://study.koolearn.com/tongyong/course_kc_data/%s/0?pathId=%s&level=1'%(str(class_id),str(pathid))
                    pathid_response = requests.get(url=get_nodeid_url, headers=self.headers, verify=False)  #
                    nodeId_datas = json.loads(pathid_response.text)
                    nodeId_list = nodeId_datas.get('data', [])
                    for nodeId_info in nodeId_list:
                        nodeId = nodeId_info.get('nodeId', '')
                        large_lesson_url = 'https://study.koolearn.com/tongyong/course_kc_data/%s/0?&level=2&learningSubjectId=%s' % (str(class_id), str(nodeId))
                        yield scrapy.Request(url=large_lesson_url, meta={'class_id': class_id, 'nodeId': nodeId}, callback=self.get_large_lesson_info)
                # else:
                #     detail_url = 'https://item.koolearn.com/m/product/leadingLive?productId={}'.format(class_id)
                #     # print('----------------%s-------------'%detail_url)
                #     yield scrapy.Request(url=detail_url, meta={'item': copy.deepcopy(item)}, callback=self.no_pathid_info)


    def get_large_lesson_info(self, response):
        class_id = response.meta.get('class_id', '')
        nodeId = response.meta.get('nodeId', '')

        data = json.loads(response.text)
        large_lesson_infos = data.get('data', [])
        for lesson_info in large_lesson_infos:
            teacherName = lesson_info.get('teacherName', '')
            lesson_nodeid = lesson_info.get('nodeId', '')
            detail_lesson_url = 'https://study.koolearn.com/tongyong/course_kc_data/%s/0?&nodeId=%s&level=3&learningSubjectId=%s'%(str(class_id), str(lesson_nodeid), str(nodeId))
            yield scrapy.Request(url=detail_lesson_url, meta={'teacherName': teacherName, 'class_id': class_id, 'nodeId': nodeId}, callback=self.get_detail_lesson_info)


    def level_4_content(self, response):
        data = json.loads(response.text)
        item = KoolearnItem()
        detail_lesson_infos = data.get('data', [])
        class_id = response.meta.get('class_id', '')
        for detail_info in detail_lesson_infos:
            lesson_live_name = detail_info.get('name', '')  #每个直播课程的名称
            lesson_teacherName = detail_info.get('teacherName', '')  #直播老师的名称
            lesson_time = detail_info.get('time', '')  #直播时间
            flag_int = detail_info.get('type', '')  #
            if flag_int == 3:
                continue
            item['class_id'] = class_id
            item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            item['lesson_name'] = lesson_live_name  # 课程名称
            # if not xx.get('lesson_live_name',''):
            #     lesson_teacherName = response.meta.get('teacherName', '')
            item['lesson_teacherName'] = lesson_teacherName  # 授课老师
            item['lesson_time'] = lesson_time  # 授课时间
            yield item

    def get_detail_lesson_info(self, response):
        data = json.loads(response.text)
        detail_lesson_infos = data.get('data', [])
        class_id = response.meta.get('class_id', '')
        nodeId = response.meta.get('nodeId', '')
        # class_id = re.search('course_kc_data/(\d+)/', response.url).group(1)
        # print('====================%s======================='%class_id)
        # item = KoolearnItem()
        item = KoolearnItem()
        for detail_info in detail_lesson_infos:
            lesson_live_name = detail_info.get('name', '')  #每个直播课程的名称
            lesson_teacherName = detail_info.get('teacherName', '')  #直播老师的名称
            lesson_time = detail_info.get('time', '')  #直播时间
            # isFinished: true
            flag_type = detail_info.get('isFinished', '')   #是否往下爬的标志
            #print(flag_type, '=====================', type(flag_type))

            if flag_type:
                flag_int = detail_info.get('type', '')   #
                if flag_int == 3:
                    continue
                item['class_id'] = class_id
                item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                item['lesson_name'] = lesson_live_name  #课程名称
                if not lesson_teacherName:
                    lesson_teacherName = response.meta.get('teacherName', '')
                item['lesson_teacherName'] = lesson_teacherName  #授课老师
                item['lesson_time'] = lesson_time  #授课时间
                yield item
            else:
                level_4_nodeid = detail_info.get('nodeId', '')  # 等级4的ID
                level_4_url = 'https://study.koolearn.com/tongyong/course_kc_data/%s/0?&nodeId=%s&level=4&learningSubjectId=%s' % (str(class_id), str(level_4_nodeid), str(nodeId))
                yield scrapy.Request(url=level_4_url, meta={'class_id': class_id}, callback=self.level_4_content)




    # def no_pathid_info(self,response):
    #     data = json.loads(response.text)
    #     detail_lesson_infos = data.get('data', [])
    #     for detail_info in detail_lesson_infos:
    #         lesson_name = detail_info.get('name', '')  #每个直播课程的名称
    #         lesson_teacherName = detail_info.get('teacher', '')  #直播老师的名称
    #         lesson_time = detail_info.get('time', '')  #直播时间
    #         item = response.meta['item']
    #         item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
    #         item['lesson_name'] = lesson_name  #课程名称
    #         item['lesson_teacherName'] = lesson_teacherName  #授课老师
    #         item['lesson_time'] = lesson_time  #授课时间
    #         yield item


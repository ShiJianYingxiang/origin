# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import datetime
import time
import codecs
import re
from koolearn.items import KoolearnItem#,Koolearn_teacherinfo_Item
from pyhive import hive



class KoolearnMobileSpider(scrapy.Spider):
    name = 'koolearn_mobile_test'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
    }
    hive_host = '172.20.207.6'
    hive_port = 10000
    hive_username = 'supdev'
    hive_database = 'default'

    def start_requests(self):
        conn = hive.Connection(host=self.hive_host, port=self.hive_port, username=self.hive_username, database=self.hive_database)
        cursor = conn.cursor()
        sql = 'select class_id,class_sub_id,start_date from dwd.dwd_education_xdfonline_class a'
        cursor.execute(sql)
        for result in cursor.fetchall():
            # print(result, type(result))

            classid = result[0]
            subclassid = result[1]
            # print(classid, '--------', subclassid)
            detail_url = 'https://item.kooup.com/product/teacher/{0}?subClassId={1}&_mobile=true'.format(classid,subclassid)
            yield scrapy.Request(url=detail_url, meta={'classid': classid, 'subclassid': subclassid}, callback=self.parse)
        # classid = '61648'
        # subclassid = '256899'
        # detail_url = 'https://item.kooup.com/product/teacher/{0}?subClassId={1}&_mobile=true'.format(classid, subclassid)
        # yield scrapy.Request(url=detail_url, meta={'classid': classid, 'subclassid': subclassid}, callback=self.parse)



    def parse(self, response):
        result = {}
        classid = response.meta.get('classid', '')
        subclassid = response.meta.get('subclassid', '')

        datas_list = json.loads(response.text).get('data','')
        remainNum = datas_list.get('remainNum', '')
        subClassId = datas_list.get('subClassId', '')
        virtualMainTeacherIds = datas_list.get('virtualMainTeacherIds', '')
        virtualMinorTeacherIds = datas_list.get('virtualMinorTeacherIds', '')
        result['remainNum'] = remainNum
        result['subClassId'] = subClassId
        result['virtualMainTeacherIds'] = virtualMainTeacherIds
        result['virtualMinorTeacherIds'] = virtualMinorTeacherIds

        data_stock_num = datas_list.get('productStockDesc', '')   #解析 productStockDesc字典
        for k, v in data_stock_num.items():
            result[k] = v

        teacher_list = datas_list.get('teachers', [])   #更新teacher_list信息
        for teacher_info in teacher_list:
            result.update(teacher_info)
        #-------------------
        result['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        result['crawl_class_id'] = classid
        result['crawl_class_sub_id'] = subclassid

        # print(result)
        file_name = '/mnt/data/weidong.shi/file/education_kooup_phone_class_detail/' + time.strftime('%Y-%m-%d') + '.json'
        # file_name = time.strftime('%Y-%m-%d') + '.json'
        with codecs.open(file_name, 'a+', encoding="utf-8") as xx:
            text = json.dumps(result, ensure_ascii=False) + '\n'
            xx.write(text)



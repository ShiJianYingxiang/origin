import scrapy
import requests
import json
import time
import logging
from leboke.items import LebokeItem
from leboke.items import LebokelessonItem

class LebokeXdfSpider(scrapy.Spider):
    name = 'leboke_xdf'
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
    logging.basicConfig(level=logging.INFO)

    def grade_list(self):
        '''
        年级列表---02
        '''
        grade_url = 'https://dfubapi.xdf.cn/system/grade.json'
        response = requests.post(url=grade_url, headers=self.headers)
        data = json.loads(response.text)
        data_list = data.get('data', [])
        grade_id_list = []
        for data_item in data_list:
            grade_id = data_item.get('code', '')
            grade_id_list.append(grade_id)
        return grade_id_list


    def quarter_list(self):
        # 获取季节------01
        url = 'https://dfubapi.xdf.cn/system/listquarter.json'
        response = requests.post(url=url, headers=self.headers)#,verify = False headers=headers
        data = json.loads(response.text)
        data_list = data.get('data', [])
        season_id_list = []
        for data_item in data_list:
            season_id = data_item.get('code', '')
            season_id_list.append(season_id)
        return season_id_list

    def citys_list(self):
        # 城市列表------01
        url = 'https://dfubapi.xdf.cn/system/campusV3.json'
        response = requests.post(url=url, headers=self.headers)#,verify = False headers=headers
        data = json.loads(response.text)
        data_list = data.get('data', [])
        city_list = []
        for data_temp in data_list:
            provinces_list = data_temp.get('provinces', [])  # 省市
            for provinces_temp in provinces_list:
                areas_list = provinces_temp.get('areas', [])  # 对应区域
                for area in areas_list:
                    cityCode = area.get('cityCode', '')  # 对应城市Code
                    city_list.append(cityCode)
        return city_list


    def start_requests(self):
        self.logger.info('------Start_requests_End_time:{}-----------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        city_list = self.citys_list()   #城市列表
        grade_list = self.grade_list()   #获取年级列表
        quarter_list = self.quarter_list()    #季度列表

        lesson_url = 'https://dfubapi.xdf.cn/class/listtomony.json'
        for city_temp in city_list:
            for grade_temp in grade_list:
                for quarter_temp in quarter_list:
                    datas = {
                        "area": city_temp,  # 对应城市   "area": 'AQ',
                        "startTimes": "",
                        "endTimes": "",
                        "grade": grade_temp,  # 对应年级的code
                        "mode": "2",
                        "pageNo": "1",
                        "pageSize": "10",
                        "quarter": quarter_temp,
                        "query": "",
                        "subjects": "",
                    }
                    yield scrapy.Request(url=lesson_url, headers=self.headers1, method='post', body=json.dumps(datas), meta={'datas': datas}, callback=self.parse)

#
    def parse(self, response):
        '''
        '''
        lesson_url = 'https://dfubapi.xdf.cn/class/listtomony.json'
        datas = response.meta.get('datas', '')   #获取传递参数
        data = json.loads(response.text)
        totalcount = data.get('page', '').get('totalCount', '')   #总的数量，判断是否用采集
        total_pages = data.get('page', '').get('pages', '')  # 总的页数，用来翻页
        if totalcount == 0:
            self.logger.info('{}---------参数下没有课程'.format(datas))
            return
        if totalcount > 0:
            for i in range(1, total_pages + 1):  # 用来控制翻页
                datas['pageNo'] = str(i)   #更改参数中对应的页数
                self.logger.info(datas)
                yield scrapy.Request(url=lesson_url, headers=self.headers1, method='post', body=json.dumps(datas), meta={'data_info': datas}, callback=self.next_detail_parse ,dont_filter=True)  #进行解析;


    def next_detail_parse(self, response):

        data = json.loads(response.text)
        data_list = data.get('data', [])
        for temp in data_list:
            classcode = temp.get('classCode', '')
            lesson_data = {
                'code': temp.get('classCode', '')
            }
            # 课程详情解析
            yield scrapy.Request(url=self.lesson_url, headers=self.headers1, method='post', meta={'classCode': classcode}, body=json.dumps(lesson_data), callback=self.lesson_info,dont_filter=True)
            #保存内容
            self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.item.update(temp)
            yield self.item
#
#
#
    def lesson_info(self,response):
        classCode = response.meta.get('classCode', '')
        data = json.loads(response.text)
        lessonitem = LebokelessonItem()
        data_list = data.get('data', [])
        if not data_list:
            lessonitem['classCode'] = classCode
            lessonitem['crawl_flag'] = 0    #crawl_flag为0 代表抓取过这个课程
            lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem

        for data_temp in data_list:
            for temp_key, temp_value in data_temp.items():
                lessonitem['classCode'] = classCode
                lessonitem[temp_key] = temp_value
                lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem
#


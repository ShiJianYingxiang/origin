# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import time
from leboke.items import LebokeSpeedItem
from leboke.items import LebokelessonItem

class LebokeSpeedSpider(scrapy.Spider):
    name = 'leboke_speed'
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

    new_headers = {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json; charset=UTF-8',
        'Cookie': 'UM_distinctid=1737e947528193-092ec64a6bcd28-1b396442-38400-1737e94752a1d3; CNZZDATA1278135745=1501185186-1595551732-%7C1595551732; X-Device-Id=55c648e574444737aa439b9b8d84da37',
        'Host': 'dfub.xdf.cn',
        'Origin': 'https://dfub.xdf.cn',
        'Referer': 'https://dfub.xdf.cn/mobile/wx/index.html',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MI 5 Build/MXB48T; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/77.0.3865.120 MQQBrowser/6.2 TBS/045227 Mobile Safari/537.36 MMWEBID/8389 MicroMessenger/7.0.16.1700(0x27001035) Process/tools WeChat/arm64 NetType/WIFI Language/zh_CN ABI/arm64',
        'X-Device-Id': '55c648e574444737aa439b9b8d84da37',
        'X-Requested-With': 'XMLHttpRequest',
        'X-Tingyun-Id': '20DitP9MmiY;r=556843452',
    }

    def citys_list(self):
        # 城市列表------01
        url = 'https://dfubapi.xdf.cn/system/campusV3.json'
        response = requests.post(url=url, headers=self.headers, verify=False)#,verify = False headers=headers
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
        city_list = self.citys_list()   #城市列表
        url = 'https://dfub.xdf.cn/speed/findgradeandsubject.json'
        for city in city_list:
            datas = {
                'areaCode': city,
                'quarterCode': "2",
                'year': time.strftime('%Y'),
            }
            yield scrapy.Request(url=url, headers=self.headers1, method='post', body=json.dumps(datas),
                             meta={'datas': datas}, callback=self.parse)

    def parse(self, response):
        parse_url = 'https://dfub.xdf.cn/speed/speedclass.json'
        city_code = response.meta.get('datas', '').get('areaCode', '')
        datas = json.loads(response.text)
        datas_list = datas.get('data', [])
        for data_temp in datas_list:
            gradeCode_str = data_temp.get('gradeCode', '')
            subjects_list = data_temp.get('subjects', [])
            subjectCode_str = ''
            for subjects_temp in subjects_list:
                subjectCode_str += subjects_temp.get('subjectCode', '')
            subjectCode_str = ','.join(subjectCode_str)
            parse_datas = {
                'areaCode': city_code,
                'gradeCode': gradeCode_str,
                'speedId': 178,
                'subjectCodes': subjectCode_str,
            }
            yield scrapy.Request(url=parse_url, headers=self.new_headers, method='post', body=json.dumps(parse_datas),
                             meta={'datas': parse_datas}, callback=self.parse_next)


    def parse_next(self, response):
        content_datas = json.loads(response.text)
        datas_list = content_datas.get('data', [])
        lesson_url = 'https://dfub.xdf.cn/class/outline.json'
        for data_temp in datas_list:
            item = LebokeSpeedItem()
            item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            item.update(data_temp)
            yield item
            classcode = data_temp.get('classCode', '')
            lesson_data = {
                'code': classcode
            }
            # 课程详情解析
            yield scrapy.Request(url=lesson_url, headers=self.headers1, method='post', meta={'classCode': classcode},
                                 body=json.dumps(lesson_data), callback=self.detail_info)


    def detail_info(self,response):
        classCode = response.meta.get('classCode', '')
        data = json.loads(response.text)
        lessonitem = LebokelessonItem()
        data_list = data.get('data', [])
        if not data_list:
            lessonitem['classCode'] = classCode
            lessonitem['crawl_flag'] = 0  # crawl_flag为0 代表抓取过这个课程
            lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem

        for data_temp in data_list:
            for temp_key, temp_value in data_temp.items():
                lessonitem['classCode'] = classCode
                lessonitem[temp_key] = temp_value
                lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            yield lessonitem

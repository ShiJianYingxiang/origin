# -*- coding: utf-8 -*-
import scrapy
import json
import time
import re
import redis
from yaodaoyun.items import YaodaoyunItem
from yaodaoyun.items import lessonItem
import requests
from lxml import etree

class WangyiyunSpider(scrapy.Spider):
    name = 'wangyiyun_old'
    # allowed_domains = ['163.com']
    # start_urls = ['http://163.com/']
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'referer': None,
    }
    lesson_url = "https://study.163.com/dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr"
    lesson_headers = {
        'origin': 'https://study.163.com',
        # 'providerid': '4713712',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400',
        'content-type': 'text/plain',
        'accept': '*/*',
        'referer': 'https://study.163.com/course/introduction.htm',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'zh-CN,zh;q=0.9',
        # 'Content-Length': '221'
    }
    get_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400',
    }
    try:
        redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=1)
    except:
        redis_db = None
    base_key = 'swd_163'
    category_id_list_key = "{}:category_id_list".format(base_key)
    error_id_set_key = "{}:error_id_set".format(base_key)
    success_id_set_key = "{}:success_id_set".format(base_key)
    success_id_list_key = "{}:success_id_list".format(base_key)
    categroy_post_url = 'https://study.163.com/p/search/studycourse.json'
    detail_url = 'https://study.163.com/course/introduction/{}.htm'
    item = YaodaoyunItem()
    lessonitem = lessonItem()

    def start_requests(self):
        for i in range(self.redis_db.llen(self.category_id_list_key)):
            category_id = self.redis_db.rpoplpush(self.category_id_list_key,self.category_id_list_key)
            category_id = category_id.decode('utf-8')

            data_info = {
                'activityId': '0',
                'frontCategoryId': category_id,
                'keyword': '',
                'orderType': '50',
                'pageIndex': '1',
                'pageSize': '50',
                'priceType': '-1',
                'relativeOffset': '0',
                'searchTimeType': '-1',
            }
            yield scrapy.Request(url=self.categroy_post_url, headers=self.headers, method='post', meta={'category_id':category_id}, body=json.dumps(data_info), callback=self.parse)

            hot_lesson_url = 'https://study.163.com/j/web/fetchPersonalData.json?categoryId=%s' % category_id
            yield scrapy.Request(url=hot_lesson_url, headers=self.get_headers, meta={'category_id': category_id},
                                 callback=self.hot_lesson_parse)

    def hot_lesson_parse(self, response):
        data = json.loads(response.text)
        category_id = response.meta.get('category_id', '')
        result = data.get('result', [])
        if result:
            for result_temp in result:
                content_lists = result_temp.get('contentModuleVo', [])
                for item in content_lists:
                    for temp_key, temp_value in item.items():
                        if temp_key == 'productId':
                            xx = self.crumb_detail(self.detail_url.format(temp_value))
                        if temp_key == 'categoryId':
                            self.item['category_id'] = category_id

                        self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        self.item[temp_key] = temp_value
                        self.item.update(xx)
                    yield self.item
        else:
            return





    def parse(self, response):
        data = json.loads(response.text)

        category_id = response.meta.get('category_id', '')
        page_nums = data.get('result', '').get('query', '').get('totlePageCount', '')
        total_nums = data.get('result', '').get('query', '').get('totleCount', '')

        data_list = data.get('result', '').get('list', [])
        for item in data_list:
            for temp_key, temp_value in item.items():
                if temp_key == 'courseId':
                    courseid = temp_value
                    xx = self.crumb_detail(self.detail_url.format(courseid))
                    self.item.update(xx)
                    payload = "callCount=1\r\nscriptSessionId=${scriptSessionId}190\r\nhttpSessionId=\r\nc0-scriptName=PlanNewBean\r\nc0-methodName=getPlanCourseDetail\r\nc0-id=0\r\nc0-param0=string:%s\r\nc0-param1=number:0\r\nc0-param2=null:null\r\nbatchId=1591429741178"%courseid
                    yield scrapy.Request(url=self.lesson_url, headers=self.lesson_headers, body=payload, method='post', meta={'courseid': courseid,'category_id':category_id},callback=self.detail_lesson_parse)

                self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.item[temp_key] = temp_value
                self.item['total_nums'] = total_nums
                self.item['category_id'] = category_id

            yield self.item

        for i in range(2, page_nums+1):
            data_info = {
                'activityId': '0',
                'frontCategoryId': category_id,
                'keyword': '',
                'orderType': '50',
                'pageIndex': str(i),
                'pageSize': '50',
                'priceType': '-1',
                'relativeOffset': str((i - 1) * 50),
                'searchTimeType': '-1'
            }
            yield scrapy.Request(url=self.categroy_post_url, headers=self.headers, method='post', meta={'category_id':category_id}, body=json.dumps(data_info), callback=self.next_page_parse, dont_filter=True)

    def next_page_parse(self, response):
        data = json.loads(response.text)
        data_list = data.get('result', '').get('list', [])
        total_nums = data.get('result', '').get('query', '').get('totleCount', '')
        category_id = response.meta.get('category_id', '')
        for item in data_list:
            for temp_key, temp_value in item.items():
                if temp_key == 'courseId':
                    courseid = temp_value
                    xx = self.crumb_detail(self.detail_url.format(temp_value))
                    self.item.update(xx)
                    payload = "callCount=1\r\nscriptSessionId=${scriptSessionId}190\r\nhttpSessionId=\r\nc0-scriptName=PlanNewBean\r\nc0-methodName=getPlanCourseDetail\r\nc0-id=0\r\nc0-param0=string:%s\r\nc0-param1=number:0\r\nc0-param2=null:null\r\nbatchId=1591429741178"%courseid
                    yield scrapy.Request(url=self.lesson_url, headers=self.lesson_headers, body=payload, method='post', meta={'courseid': courseid, 'category_id': category_id}, callback=self.detail_lesson_parse)

                self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.item['total_nums'] = total_nums
                self.item[temp_key] = temp_value
                self.item['category_id'] = category_id

            yield self.item


    def detail_lesson_parse(self,response):
        category_id = response.meta.get('category_id', '')
        courseid = response.meta.get('courseid', '')
        data_lsit = re.findall(r"(?s)\s*(audioTime.*?fee=.*?;)", response.text)
        try:
            for item in data_lsit:
                re_text = re.sub(" |\t|\n|\r|\r\n", '', item).strip()
                re_text = re.sub(';s\d+\.', '&', re_text).strip(';')
                lesson_str = re_text.split('&')
                for temp in lesson_str:
                    if temp:
                        temp_split = temp.split('=')
                        key = temp_split[0]
                        if key == 'description' or key == 'lessonName':
                            value = temp_split[1].replace('"', '').encode('utf-8').decode("unicode_escape")
                        elif key == 'photoUrl':
                            value = temp_split[1].replace('"', '')
                        else:
                            value = temp_split[1]
                        self.lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        self.lessonitem[key] = value
                        self.lessonitem['category_id'] = category_id
                        self.lessonitem['courseid'] = courseid
                yield self.lessonitem
        except Exception as e:
            self.logger.error(e, '================', courseid)
            self.redis_db.sadd(self.error_id_set_key, courseid)
            self.lessonitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.lessonitem[key] = key
            self.lessonitem['category_id'] = category_id
            self.lessonitem['courseid'] = courseid
            yield self.lessonitem

    def crumb_detail(self, detail_url):

        detail_id = re.search('introduction/(\d+)\.htm', detail_url).group(1)
        # introduction/1005603020.htm
        response = requests.get(url=detail_url,headers=self.get_headers)
        # html = response.content.decode(self.encode)   #进行编码
        response = etree.HTML(response.content)
        breadcrumb = response.xpath('''//ul[@class="g-flow"]//li//a''')

        breadcrumb_dict_content = {}
        breadcrumb_dict = {}
        for breadcrumb_temp in breadcrumb:
            breadcrumb_content = breadcrumb_temp.xpath('''./text()''')[0]
            breadcrumb_id = breadcrumb_temp.xpath('''./@href''')[0]
            # print(breadcrumb_content, '==============', breadcrumb_id)
            if breadcrumb_content == '首页':
                breadcrumb_id = 'top_id'

            elif breadcrumb_content == '课程详情':
                breadcrumb_id = detail_id
            else:
                # if 'category' in breadcrumb_id:
                breadcrumb_category_id = re.search(r'category/(\d+)', breadcrumb_id).group(1)
                # print(breadcrumb_category_id)
                breadcrumb_id = breadcrumb_category_id
            breadcrumb_dict_content[breadcrumb_content] = breadcrumb_id
            breadcrumb_dict['breadcrumb_dict'] = breadcrumb_dict_content

        return breadcrumb_dict

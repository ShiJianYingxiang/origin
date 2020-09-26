# -*- coding: utf-8 -*-
import scrapy
import json
import time
import re
import redis
from yaodaoyun.items import YaodaoyunItem
from yaodaoyun.items import lessonItem
import requests
import copy
from lxml import etree

class WangyiyunSpider(scrapy.Spider):
    name = 'wangyiyun_2'
    # allowed_domains = ['163.com']
    # start_urls = ['http://163.com/']
    custom_settings = {
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': './././Log/scrapy_{}_{}.log'.format('wangyiyun_2', time.strftime('%Y-%m-%d'))
    }
    get_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400',
        'referer': None,
    }
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
    try:
        redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        redis_db = None
    base_key = 'swd_163'
    category_id_list_key = "{}:category_id_list".format(base_key)
    error_id_set_key = "{}:error_id_set".format(base_key)
    categroy_post_url = 'https://study.163.com/p/search/studycourse.json'
    item = YaodaoyunItem()
    lessonitem = lessonItem()


    def start_requests(self):
        self.logger.info('---------开始时间：{}-------------------'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        # category_id_list = ['480000003130014', '480000003130013', '480000003124008', '480000003124009', '480000003123021', '480000003134007', '480000003119011', '480000003122009', '480000003121009', '480000003132006', '480000003132007', '480000003128005', '480000003130008', '480000003123019', '480000003134001', '480000003132003', '480000003125014', '480000003128006', '480000003131006', '480000003129015', '480000003127008', '480000003120003', '480000003130009', '480000003134002', '480000003131005', '480000003121003', '480000003121055', '480000003132060', '480000003132061', '480000003120055', '480000003130075', '480000003132062', '480000003127059', '480000003127060', '480000003124058', '480000003121057', '480000003134059', '480000003121056', '480000003126063', '480000003124057', '480000003124059', '480000003128048', '480000003122052', '480000003127061', '480000003134060', '480000003128049', '480000003120053', '480000003123059', '480000003129072', '480000003129073', '480000003126062', '480000003125063', '480000003134058', '480000003127067', '480000003125069', '480000003125070', '480000003126067', '480000003131061', '480000003129074', '480000003121058', '480000003120054', '480000003134061', '480000003130083', '480000003123066', '480000003130084', '480000003123067', '480000003127057', '480000003123061', '480000003122053', '480000003120022', '480000003129033', '480000003124024', '480000003130031', '480000003131026', '480000003121021', '480000003123035', '480000003129034', '480000003131027', '480000003130032', '480000003120024', '480000003128024', '480000003132022', '480000003120023', '480000003132023', '480000003132024', '480000003132025', '480000003120025', '480000003123034', '480000003121022', '480000003120027', '480000003121023', '480000003132026', '480000003124023', '480000003122022', '480000003126029', '480000003134017', '480000003120028', '480000003127033', '480000003127068', '480000003124065', '480000003126069', '480000003249007', '480000003132070', '480000003124036', '480000003126038', '480000003225021', '480000003126044', '480000003234020', '480000003125035', '480000003229030', '480000003227018', '480000003230018', '480000003126039', '480000003234021', '480000003238019', '480000003228017', '480000003228018', '480000003123043', '480000003130055', '480000003130056', '480000003130057', '480000003120039', '480000003132037', '480000003123049', '480000003125042', '480000003237017', '480000003134038', '480000003134039', '480000003130058', '480000003237018', '480000003121036', '480000003128038', '480000003125043', '480000003128039', '480000003130059', '480000003128036', '480000003134040', '480000003121039', '480000003232023', '480000003130047', '480000003134041', '480000003126047', '480000003132045', '480000003127036', '480000003131044', '480000003134042', '480000003130061', '480000003130062', '480000003134029', '480000003126049', '480000003127042', '480000003134030', '480000003123050', '480000003121041', '480000003119045', '480000003121042', '400000001321001', '400000001331001', '400000001331002', '400000001328002', '400000001331003', '400000001322001', '400000001324001', '480000003131070', '480000003125075', '400000001326002', '400000001329001', '400000001322002', '400000001326001', '400000001328001', '400000001374005', '400000001370002', '400000001372006', '400000001367005', '400000001374004', '400000001365005', '400000001367004', '400000001377002', '400000001375003', '480000003408002', '480000003435002', '480000003409005', '480000003435001', '480000003436001', '400000001324003', '480000003411005', '400000001325002', '480000003121047', '480000003131065', '480000003125071', '480000003123068', '480000003135001', '480000003127045', '480000003127046', '480000003129066', '480000003134050', '480000003120045', '480000003132053', '480000003120046', '480000003132052', '480000003126054', '480000003131050', '480000003129068', '480000003121048', '480000003131048', '480000003120047', '480000003134052', '480000003126055', '480000003127047', '480000003125054', '480000003129067', '480000003123056', '480000003123057', '480000003128043', '480000003131051', '480000003134051', '480000003132054', '480000003134049', '480000003120048', '480000003127048', '480000003130068', '480000003121049', '480000003129069', '480000003127049', '480000003124053', '480000003120044', '480000003131052', '480000003134053', '480000003125055', '480000003130070', '480000003131053', '480000003131049', '480000003122047', '480000003120049', '480000003126057', '480000003131055', '480000003134054', '480000003128044', '480000003121051', '480000003130069', '480000003125058', '480000003132057', '480000003127053', '480000003127052', '480000003134055', '480000003127054', '480000003124025', '480000003121024', '480000003125030', '480000003128025', '480000003132028', '480000003125031', '480000003123036', '480000003124027', '480000003124028', '480000003132030', '480000003122026', '480000003127028', '480000003132031', '480000003122027', '480000003123037', '480000003121028', '480000003131028', '480000003127027', '480000003129038', '480000003122023', '480000003122024', '480000003122025', '480000003134018', '480000003121026', '480000003121027', '480000003131030', '480000003134019', '480000003130034', '480000003129037', '480000003124026', '480000003131029', '480000003134021', '480000003126030', '480000003126031', '480000003130033', '480000003132029', '480000003134020', '480000003119028', '480000003119029', '480000003129036', '480000003128026', '480000003121025', '480000003125052', '480000003128042', '480000003131047', '480000003134048', '480000003126053', '480000003132051', '480000003124052', '480000003121004', '480000003131009', '480000003121007', '480000003132004', '480000003130011', '480000003130012', '480000003121008', '480000003119009', '480000003129017', '480000003120007', '480000003122008', '480000003129019', '480000003131013', '480000003126016', '480000003131010', '480000003126017', '480000003120006', '480000003125016', '480000003130010', '480000003124005', '480000003128007', '480000003134005', '480000003120005', '480000003121005', '480000003121006', '480000003119008', '480000003131012', '480000003127010', '480000003129020', '480000003124010', '480000003129021']
        category_id_list = self.redis_db.lrange(self.category_id_list_key, 220, -1)
        for category_id in category_id_list:
            if isinstance(category_id, bytes):
                category_id = category_id.decode()
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
            self.logger.info('----开始请求分类---{}----'.format(category_id))
            yield scrapy.Request(url=self.categroy_post_url, headers=self.headers, method='post', meta={'category_id':category_id}, body=json.dumps(data_info), callback=self.parse, dont_filter=True)

            hot_lesson_url = 'https://study.163.com/j/web/fetchPersonalData.json?categoryId=%s'%category_id
            yield scrapy.Request(url=hot_lesson_url, headers=self.get_headers, meta={'category_id': category_id}, callback=self.hot_lesson_parse)


    def hot_lesson_parse(self, response):
        data = json.loads(response.text)
        category_id = response.meta.get('category_id', '')
        result = data.get('result', [])
        self.logger.info('----请求分类(热门)---{}----'.format(category_id))
        if result:
            for result_temp in result:
                content_lists = result_temp.get('contentModuleVo', [])
                for item in content_lists:
                    courseId = item.get('productId', '')  # 获取所有的课程id，进行请求课次的操作
                    payload = "callCount=1\r\nscriptSessionId=${scriptSessionId}190\r\nhttpSessionId=\r\nc0-scriptName=PlanNewBean\r\nc0-methodName=getPlanCourseDetail\r\nc0-id=0\r\nc0-param0=string:%s\r\nc0-param1=number:0\r\nc0-param2=null:null\r\nbatchId=1591429741178" % courseId
                    self.logger.info('----请求课程(热门)---{}----'.format(courseId))
                    yield scrapy.Request(url=self.lesson_url, headers=self.lesson_headers, body=payload, method='post', meta={'courseid': courseId, 'category_id': category_id},callback=self.detail_lesson_parse, dont_filter=True)

                    self.item.update(item)
                    self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.item['category_id'] = category_id
                    yield self.item



    def parse(self, response):
        category_id = response.meta.get('category_id', '')
        data = json.loads(response.text)
        page_nums = data.get('result', '').get('query', '').get('totlePageCount', '')   #获取总页数
        self.logger.info('----分类{}--的页数是--{}----'.format(category_id,page_nums))
        for i in range(1, page_nums+1):
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
            self.logger.info(data_info)
            yield scrapy.Request(url=self.categroy_post_url, headers=self.headers, method='post', meta={'category_id': category_id}, body=json.dumps(data_info), callback=self.next_page_parse, dont_filter=True)#, dont_filter=True


    def next_page_parse(self, response):
        category_id = response.meta.get('category_id', '')
        self.logger.info('----开始解析详情页------')

        data = json.loads(response.text)  #翻页获取的data
        data_list1 = data.get('result', '').get('list', [])  #解析的内容

        if not data_list1:
            return
        for item in data_list1:
            '''获取到数据，将数据进行传递'''
            courseId = item.get('productId', '')  # 获取所有的课程id，进行请求课次的操作
            payload = "callCount=1\r\nscriptSessionId=${scriptSessionId}190\r\nhttpSessionId=\r\nc0-scriptName=PlanNewBean\r\nc0-methodName=getPlanCourseDetail\r\nc0-id=0\r\nc0-param0=string:%s\r\nc0-param1=number:0\r\nc0-param2=null:null\r\nbatchId=1591429741178" % courseId
            yield scrapy.Request(url=self.lesson_url, headers=self.lesson_headers, body=payload, method='post', meta={'courseid': courseId, 'category_id': category_id},callback=self.detail_lesson_parse, dont_filter=True)


            self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
            self.item.update(item)
            self.item['category_id'] = category_id
            yield self.item


    def detail_lesson_parse(self,response):
        category_id = response.meta.get('category_id', '')
        courseid = response.meta.get('courseid', '')


        data_lsit = re.findall(r"(?s)\s*(audioTime.*?fee=.*?;)", response.text)
        self.logger.info('----{}课程有{}详情课次------'.format(courseid, len(data_lsit)))
        try:
            for item in data_lsit:
                re_text = re.sub(r'(s\d+\.)', '', item).strip()
                re_text = re.sub(r'(\r\n)', '', re_text).strip()
                lesson_str = re_text.split(';')
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
            print(e)
            self.logger.error(courseid)
            pass




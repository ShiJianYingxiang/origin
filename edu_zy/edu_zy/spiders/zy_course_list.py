# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
import redis
import codecs
from edu_zy.items import EduZyCourseBatchItem,EduZyItem


class ZyCourseListSpider(scrapy.Spider):
    name = 'zy_course_list'
    custom_settings = {
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': './././Log/scrapy_{}_{}.log'.format('zhuoyue', time.strftime('%Y-%m-%d'))
    }
    format_url = 'https://kc.zy.com/courses/index/c/{}/0/0/0/0/0/0/0/{}'
    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Host': 'kc.zy.com',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        'referer': 'None',
    }
    try:

        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None

    def start_requests(self):
        url = 'https://kc.zy.com/courses/index/c/2/0/0/0/0/0/0/0/0'
        yield scrapy.Request(url=url, headers=self.headers, callback=self.get_city)


    def get_city(self, response):
        ori_url = 'https://kc.zy.com/courses/index/c/{}/0/0/0/0/0/0/0/0'
        citys_list = response.xpath('''//div[@class="c_menu"]//div[@class="m_item"]''')#.extract()
        for citys_item in citys_list:
            citys_info = {}
            citys_id = citys_item.xpath('''./@item-value''').extract()[0]
            req_url = ori_url.format(citys_id)

            citys_name = citys_item.xpath('''./a/span/text()''').extract()[0]
            citys_info['city_name'] = citys_name
            citys_info['city_id'] = citys_id

            yield scrapy.Request(url=req_url, headers=self.headers, meta={'citys_info': citys_info}, callback=self.parse)


    def parse(self, response):
        citys_info = response.meta.get('citys_info', '')
        citys_id = response.meta.get('citys_info', '').get('city_id', '')
        citys_name = response.meta.get('citys_info', '').get('city_name', '')


        all_page_nums = re.search(r'\s*pages\s*[\'\"]\s*[:：](\d+)', response.text).group(1)
        self.logger.info('{}的总页数是{}'.format(citys_name, all_page_nums))
        for page in range(1, int(all_page_nums)+1):
            req_url = self.format_url.format(citys_id, str(page))
            #if '/31/' not in req_url:
            #    continue
            #print(req_url, '**********************')
            yield scrapy.Request(url=req_url, headers=self.headers, meta={'citys_info': citys_info, 'all_page_nums': all_page_nums, 'page': page}, callback=self.all_course_list)


    def all_course_list(self, response):
        now_page = response.meta.get('page', '')
        citys_info = response.meta.get('citys_info', '')
        citys_id = response.meta.get('citys_info', '').get('city_id', '')
        citys_name = response.meta.get('citys_info', '').get('city_name', '')
        all_page_nums = response.meta.get('all_page_nums', '')

        prince_headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'referer': 'None',
        }
        all_course_href_list = response.xpath('''//div[@class="m_btn"]//a[@class="alinebtn base"]/@href''').extract()
        self.logger.info('{}的总页数是{},当前是第{}页获取的课程数是{}'.format(citys_name, all_page_nums, now_page, len(all_course_href_list)))
        for course_href_item in all_course_href_list:
            course_price_url = 'https://kc.zy.com/course/ps/claPS.json?claIds%5B%5D=' + course_href_item.replace('/course/', '')
            yield scrapy.Request(url=course_price_url, headers=prince_headers, meta={'citys_info': citys_info}, callback=self.parse_price_detail)


    def parse_price_detail(self, response):
        citys_info = response.meta.get('citys_info', '')
        citys_id = response.meta.get('citys_info', '').get('city_id', '')
        citys_name = response.meta.get('citys_info', '').get('city_name', '')

        json_data = json.loads(response.text)
        data = json_data.get('data', [])[0]
        bizSystemId = data.get('bizSystemId', '')
        claId = data.get('claId', '')
        # print(bizSystemId, claId, data)
        detail_url = 'https://kc.zy.com/course/{}_{}'.format(bizSystemId, claId)
        yield scrapy.Request(url=detail_url, headers=self.headers, meta={'price_info': data, 'citys_info': citys_info}, callback=self.parse_detail)


    def parse_detail(self,response):
        course_detail_item = EduZyItem()

        citys_info = response.meta.get('citys_info', '')
        citys_id = response.meta.get('citys_info', '').get('city_id', '')
        citys_name = response.meta.get('citys_info', '').get('city_name', '')

        batch_time = time.strftime('%Y-%m-%d %H') + ':00:00'  # 批次时间
        crawl_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 抓取时间
        price_info = response.meta.get('price_info', '')  #价格信息

        #配额状态
        surplusQuota = price_info.get('surplusQuota', '')
        claFee = price_info.get('claFee', '')
        claId = price_info.get('claId', '')
        claMaterialFee = price_info.get('claMaterialFee', '')
        afterDiscountPrice = price_info.get('afterDiscountPrice', '')

        # 现在展示的价格(红色字体-price)
        if afterDiscountPrice:    #有折扣状态
            price = claMaterialFee
            ori_price = claFee + claMaterialFee    #原价
        else:
            price = claFee + claMaterialFee
            ori_price = price

        #解析课程详细信息
        #课程名称
        course_title = response.xpath('''//div[@class="l_name"]//span/text()''').extract()[0]
        # 课程标签(黄色框)
        if 'class="baseYellowColor"' in response.text:
            course_tag = response.xpath('''//span[@class="baseYellowColor"]/text()''').extract()[0]
        else:
            course_tag = ''
        #课程老师名称
        course_teacher = response.xpath('''(//div[@class="d_table"]//tr//td/span)[1]/text()''').extract()[0]
        course_teacher = course_teacher.strip().replace('\n', '').replace(' ', '').replace('老师', '').replace('：', '').replace(':', '')
        #课程年级
        course_grade = response.xpath('''(//div[@class="d_table"]//tr//td/span)[2]/text()''').extract()[0]
        course_grade = course_grade.strip().replace('\n', '').replace(' ', '').replace('年级：', '').replace('年级:', '')
        #课程学期
        course_term = response.xpath('''(//div[@class="d_table"]//tr//td/span)[3]/text()''').extract()[0]
        course_term = course_term.strip().replace('\n', '').replace(' ', '').replace('学期', '').replace('：', '').replace(':', '')
        # 课程讲数
        course_nums = response.xpath('''(//div[@class="d_table"]//tr//td/span)[4]/text()''').extract()[0]
        course_nums = course_nums.strip().replace('\n', '').replace(' ', '').replace('讲数', '').replace('：', '').replace(':', '')
        # 课程产品
        course_product = response.xpath('''(//div[@class="d_table"]//tr//td/span)[5]/text()''').extract()[0]
        course_product = course_product.strip().replace('\n', '').replace(' ', '').replace('产品', '').replace('：', '').replace(':', '')
        # 课程校区
        course_campus = response.xpath('''(//div[@class="d_table"]//tr//td/span)[6]/text()''').extract()[0]
        course_campus = course_campus.strip().replace('\n', '').replace(' ', '').replace('校区：', '').replace('校区:', '')
        # 电话
        course_tel = response.xpath('''(//div[@class="d_table"]//tr//td/span)[7]/text()''').extract()[0]
        course_tel = course_tel.strip().replace('\n', '').replace('电话：', '').replace('电话:', '')
        # 课程时间
        course_time = response.xpath('''(//div[@class="d_table"]//tr//td/span)[8]/text()''').extract()[0]
        course_time = course_time.strip().replace('时间：', '').replace('时间:', '').replace('\r\n', ' ').replace('\t', '')
        # 地址
        course_address = response.xpath('''(//div[@class="d_table"]//tr//td/span)[9]/text()''').extract()[0]
        course_address = course_address.strip().replace('\n', '').replace(' ', '').replace('地址', '').replace('：', '').replace(':', '')

        try:
            xx = response.text.split('traceCourseDetail(')[-1].split(');')[0].strip()
            add_info = json.loads(xx)
        except:
            add_info = ''
            

        course_detail_item['course_url'] = response.url
        course_detail_item['city_name'] = citys_name
        course_detail_item['city_id'] = citys_id
        course_detail_item['course_title'] = course_title
        course_detail_item['claMaterialFee'] = claMaterialFee
        course_detail_item['claFee'] = claFee
        course_detail_item['claId'] = claId
        course_detail_item['course_tag'] = course_tag
        course_detail_item['course_teacher'] = course_teacher
        course_detail_item['course_grade'] = course_grade
        course_detail_item['course_term'] = course_term
        course_detail_item['course_nums'] = course_nums
        course_detail_item['course_product'] = course_product
        course_detail_item['course_campus'] = course_campus
        course_detail_item['course_tel'] = course_tel
        course_detail_item['course_time'] = course_time
        course_detail_item['course_address'] = course_address
        course_detail_item['surplusQuota'] = surplusQuota
        course_detail_item['now_price'] = price
        course_detail_item['ori_price'] = ori_price
        course_detail_item['afterDiscountPrice'] = afterDiscountPrice
        course_detail_item['crawl_source'] = 'list'
        course_detail_item['batch_time'] = batch_time
        course_detail_item['crawl_time'] = crawl_time
        course_detail_item.update(add_info)
        yield course_detail_item

        # 课程表
        course_lists = response.xpath('''//div[@class="J_gridCalendar"]//div[contains(@class,"i_list")]//div''')#.extract()
        course_info_dict = dict()
        for course_item in course_lists:
            course_detail_id = course_item.xpath('''./a/b/text()''').extract()[0]
            course_detail_time = course_item.xpath('''./a/span/text()''').extract()[0]
            course_detail_time = course_detail_time.replace('\r\n', ' ').replace('\t', '')
            course_info_dict[course_detail_id] = course_detail_time



        time_dict = course_info_dict
        list_key = list()
        list_value = list()
        ori_list_value = list()
        for key in time_dict.keys():
            list_key.append(key)
        for value in time_dict.values():
            value = value.replace('月', '-').replace('日', '').strip()
            list_value.append(value)
            ori_list_value.append(value)

        year = 2020
        s1 = list_value[0]
        flag = s1
        list_value[0] = "{0}-{1}".format(year, list_value[0])
        for i in range(1, len(list_value)):
            if list_value[i] < flag:
                year += 1
                flag = list_value[i]
            list_value[i] = "{0}-{1}".format(year, list_value[i])

        file_name = '/mnt/data/weidong.shi/file/education_zhuoyue_lesson/' + time.strftime('%Y-%m-%d') + '.txt'
        #file_name = time.strftime('%Y-%m-%d') + '.txt'

        for time_key, time_value, time_ori_value in zip(list_key, list_value, ori_list_value):
            course_list_item = dict()
            course_list_item['course_url'] = response.url
            course_list_item['claId'] = claId
            course_list_item['course_title'] = course_title
            course_list_item['course_nums'] = course_nums
            course_list_item.update(citys_info)
            course_list_item['batch_time'] = batch_time
            course_list_item['crawl_time'] = crawl_time
            course_list_item['lesson_num'] = time_key
            course_list_item['lesson_date'] = time_value
            course_list_item['lesson_value'] = time_ori_value


            with codecs.open(file_name, 'a+', encoding="utf-8") as xx:
                text = json.dumps(dict(course_list_item), ensure_ascii=False) + '\n'
                xx.write(text)












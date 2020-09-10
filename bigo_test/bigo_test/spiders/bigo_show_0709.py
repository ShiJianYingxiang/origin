# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import time
from bigo_test.items import BigoTestItem
import redis

class BigoShowSpider(scrapy.Spider):
    name = 'bigo_show_bak'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    headers1 = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    url = 'https://www.bigo.tv/openOfficialWeb/vedioList/5'
    item = BigoTestItem()
    #ln -s /usr/local/python3/bin /usr/bin/scrapy
    redishandler = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)

    def start_requests(self):
        #country_url = 'https://www.bigolive.tv/openInterface/getCountryInfoList'
        #response = requests.get(url=country_url, headers=self.headers)
        #print(response.text)
        #data_list = json.loads(response.text)
        #country_areas = data_list.get('data', '')
        ids = ["WF", "JP", "JM", "JO", "WS", "GW", "GU", "GT", "GR", "GQ", "GP", "GY", "GF", "GE", "GD", "GB", "GA",
               "GN", "GM", "GL",
               "GI", "GH", "PR", "PS", "PW", "PT", "PY", "PA", "PF", "PG", "PE", "PK", "PH", "PN", "PL", "PM", "ZM",
               "ZA", "ZW", "ME",
               "MD", "MG", "MF", "MA", "MC", "MM", "ML", "MO", "MN", "MH", "MK", "MU", "MT", "MW", "MV", "MQ", "MP",
               "MS", "MR", "MY",
               "MX", "MZ", "FR", "FI", "FJ", "FK", "FM", "FO", "CK", "CI", "CH", "CO", "CN", "CM", "CL", "CC", "CA",
               "CG", "CF", "CD",
               "CZ", "CY", "CX", "CR", "CV", "CU", "SZ", "SY", "SS", "SR", "SV", "ST", "SK", "SI", "SH", "SO", "SN",
               "SM", "SL", "SC",
               "SB", "SA", "SG", "SE", "SD", "YE", "YT", "LB", "LC", "LA", "LK", "LI", "LV", "LT", "LU", "LR", "LS",
               "LY", "VA", "VC",
               "VE", "VG", "IQ", "VI", "IS", "IR", "IT", "VN", "IM", "IL", "IN", "IE", "ID", "BD", "BE", "BF", "BG",
               "BA", "BB", "BL",
               "BM", "BN", "BO", "BH", "BI", "BJ", "BT", "BW", "BR", "BS", "BY", "BZ", "RU", "RW", "RS", "RO", "OM",
               "HR", "HT", "HU",
               "HK", "HN", "EE", "EG", "EC", "ET", "ES", "ER", "UY", "UZ", "US", "UG", "UA", "VU", "NI", "NL", "NO",
               "NA", "NC", "NE",
               "NG", "NZ", "NP", "NR", "NU", "KG", "KE", "KI", "KH", "KN", "KM", "KR", "KP", "KW", "KZ", "KY", "DO",
               "DM", "DJ", "DK",
               "DG", "DE", "DZ", "TZ", "TV", "TW", "TT", "TR", "TN", "TO", "TL", "TM", "TJ", "TK", "TH", "TG", "TD",
               "TC", "AE", "AD",
               "AG", "AF", "AI", "AM", "AL", "AO", "AN", "AQ", "AS", "AR", "AU", "AT", "AW", "AZ", "QA"] 
        for country_area in ids:
            datas = {
                'ignoreUids': '1578156944',
                'tabType': country_area,
            }

            yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas, meta={"country": country_area}, callback=self.parse)

    def parse(self, response):
        country_area = response.meta.get('country', '')
        next_page_parms = response.meta.get('next_page_parms', '')
        #self.logger.error(response.status_code,'================================')

        data = json.loads(response.text)

        post_data = ''
        if data is not None:
            for data_1 in data:
                detail_link = 'http://www.bigolive.tv/' + str(data_1['bigo_id'])   #第一次请求
                
                # yield scrapy.Request(url=detail_link, meta={'datas': data_1, "country": country_area}, headers=self.headers, callback=self.parse_bean)   #将解析的data传递至parse_bean
                owner = '.' + str(data_1['owner'])   #拼接参数
                post_data += owner   #拼接参数
                self.redishandler.rpush('bigo_spider:items', data_1['bigo_id'])

            post_data = next_page_parms + post_data
            if len(data) == 30:
                datas = {
                    'tabType': country_area,
                    'ignoreUids': '1578156944' + post_data,
                }
                self.logger.error(datas)
                yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas,
                                         meta={"country": country_area, 'next_page_parms': post_data}, callback=self.parse, dont_filter=True)
    #


    def parse_bean(self, response):

        data_json = response.meta.get('datas', '')
        country = response.meta.get('country', '')
        batch = time.strftime('%Y-%m-%d %H') + ':00:00'
        contribution_value = response.xpath('//i[@class="beans"]/text()').get()

        extras = {}
        self.item['cat1'] = '秀场'
        self.item['cat2'] = ''
        self.item['uid'] = str(data_json['room_id'])
        self.item['online'] = data_json['user_count']
        self.item['nickname'] = data_json['nick_name']
        self.item['platform'] = 'bigo'
        self.item['fans'] = ''
        self.item['contribution'] = contribution_value
        self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        self.item['batch'] = batch
        extras['owner'] = data_json['owner']
        extras['bigo_id'] = data_json['bigo_id']
        extras['country'] = country
        # extras['country_name'] = data_json['country_name']
        self.logger.info(extras)
        self.item['extras'] = extras
        yield self.item

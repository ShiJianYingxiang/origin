# -*- coding: utf-8 -*-
import scrapy
import redis
import codecs
import json
import time
import datetime
import requests

class BigoShowSpider(scrapy.Spider):
    name = 'bigo_show_new'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    headers1 = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    url = 'https://www.bigo.tv/openOfficialWeb/vedioList/5'
    retry_count = 3

    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'bigo_id_spider'

    #bigo_id_item_set = '{}:item_set'.format(base_key)
    bigo_id_item_list = '{}:item_list'.format(base_key)
    today_time = time.strftime('%m-%d_%H', time.localtime(time.time()))
    bigo_id_item_set = '{}:{}_set'.format(base_key, today_time)

    def start_requests(self):
        # 发送区域的请求
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

        for item in ids:
            datas = {
                'ignoreUids': '1578156944',
                'tabType': item,
            }
            yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas, meta={"country": item}, callback=self.parse)
    #     JP
    #     datas = {
    #         'ignoreUids': '1578156944',
    #         'tabType': 'JP',
    #     }
    #     yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas, meta={"country": 'JP'},
    #                              callback=self.parse)

    def parse(self, response):
        country_area = response.meta.get('country', '')
        next_page_parms = response.meta.get('next_page_parms', '')
        batch = time.strftime('%Y-%m-%d %H') + ':00:00'
        retry_count = response.meta.get('retry_count', 0)  #
        error_occurred = False
        if response.text == '[]':
            self.logger.info('{} 该区域下请求返回数据为空'.format(country_area))
            return        

        json_data = json.loads(response.text)
        try:
            print(type(response.text),'11111111111111111111')
            json_data = json.loads(response.text)
            #print(type(json_data),'*******************')
            assert len(json_data) > 0, '区域下详情为空!!'
        except Exception as e:
            self.logger.info('请求 {} 详情信息失败,错误信息:{}, 原始返回内容:{}'.format(country_area, e, json_data))
            error_occurred = True
            #return None

        if error_occurred and retry_count < self.retry_count:   #对下载出错的进行重试下载
            datas = {
                'ignoreUids': '1578156944',
                'tabType': country_area,
            }
            yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas, meta={"country": country_area,'retry_count': retry_count + 1},
                                     callback=self.parse)



        post_data = ''
        extras = {}
        data_item = {}
        if json_data is not None:
            for data_1 in json_data:
                # detail_link = 'http://www.bigolive.tv/' + str(data_1['bigo_id'])   #第一次请求
                data_item['uid'] = str(data_1['bigo_id'])
                data_item['online'] = ''
                data_item['nickname'] = data_1['nick_name']
                data_item['platform'] = 'bigo'
                data_item['fans'] = ''
                # data_item['contribution'] = contribution_value   #贡献值
                #data_item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
                data_item['batch'] = batch
                extras['owner'] = data_1['owner']
                extras['bigo_id'] = data_1['bigo_id']
                extras['country'] = data_1['country_name']
                data_item['extras'] = extras
                redis_data = json.dumps(data_item)
                if not self.url_db.sismember(self.bigo_id_item_set, redis_data):   #去重key
                    self.url_db.sadd(self.bigo_id_item_set, redis_data)
                    self.url_db.lpush(self.bigo_id_item_list, redis_data)

                owner = '.' + str(data_1['owner'])   #拼接参数
                post_data += owner   #拼接参数

            post_data = next_page_parms + post_data
            if len(json_data) == 30:
                datas = {
                    'tabType': country_area,
                    'ignoreUids': '1578156944' + post_data,
                }
                self.logger.error(datas)
                yield scrapy.FormRequest(url=self.url, headers=self.headers1, formdata=datas, meta={"country": country_area, 'next_page_parms': post_data}, callback=self.parse, dont_filter=True)

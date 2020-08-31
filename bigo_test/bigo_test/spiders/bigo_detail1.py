# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import time
from bigo_test.items import BigoTestItem
import redis

class BigoDetailSpider(scrapy.Spider):
    name = 'bigo_detail'
    # allowed_domains = ['bigotv.tv']
    # start_urls = ['http://bigotv.tv/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'
    }
    headers1 = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    # url = 'http://www.bigolive.tv/{}'
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'bigo_id_spider'
    bigo_id_item_set = '{}:item_set'.format(base_key)
    bigo_id_item_list = '{}:item_list'.format(base_key)
    item = BigoTestItem()

    def start_requests(self):
        str_len = self.url_db.llen(self.bigo_id_item_list)
        for i in range(str_len):
            bigo_id_json = self.url_db.lpop(self.bigo_id_item_list)
            # if bigo_id_json is None:
            #     return
            each = json.loads(bigo_id_json, encoding='utf-8')
            link = 'http://www.bigo.tv/' + str(each.get('extras', '').get('bigo_id', ''))
            # print(link)
            yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)



    def parse(self, response):
        data_json = response.meta.get('datas', '')
        contribution_value = response.xpath('//i[@class="beans"]/text()').get()
        data_json['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))   #抓取时间
        data_json['contribution'] = contribution_value

        for item_key, item_value in data_json.items():
            self.item[item_key] = item_value
            self.item['cat1'] = '秀场'
            self.item['cat2'] = ''
            print(self.item)
            yield self.item

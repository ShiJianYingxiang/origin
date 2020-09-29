# -*- coding: utf-8 -*-
import scrapy
import json
import math
import time
# MaidanglaoItem
from maidanglao.items import MaidanglaoItem

class GetCitysSpider(scrapy.Spider):
    name = 'get_citys'
    # allowed_domains = ['maidanglao.com']
    # start_urls = ['http://maidanglao.com/']

    custom_settings = {
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': '././././Log/scrapy_{}_{}.log'.format('maidanglao', time.strftime('%Y-%m-%d'))
    }

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.80 Safari/537.36',
        'Content-Type': 'application/json',
    }
    city_url = 'https://yuntuapi.amap.com/datasearch/local?filter=HasMobileOrdering%3A1&tableid=55c45e91e4b0cae7dbedd9b8&key=27819cd48a7baedac518c9ab87f21328&page={}&limit=75&keywords=&city={}'


    def start_requests(self):
        url = 'https://mcdmap-dc.can-dao.com/client'
        data = {
            "actionId": 1,
            "content": "{}",
            "serviceId": 1,
        }
        yield scrapy.Request(url=url, headers=self.headers, method='post', body=json.dumps(data), callback=self.parse)


    def parse(self, response):
        json_data = json.loads(response.text)
        city_list = json_data.get('data', [])
        self.logger.info('获取的城市个数是 {}'.format(len(city_list)))
        for city_item in city_list:
            city_name = city_item.get('cityName', '')
            if '测试' in city_name:
                continue
            city_url = self.city_url.format(1, city_name)
            self.logger.info('开始抓取{}的店铺'.format(city_name))
            yield scrapy.Request(url=city_url, headers=self.headers, meta={'city_name': city_name, 'item': city_item}, callback=self.city_to_shop)
        # city_name = '%E4%B8%8A%E6%B5%B7%E5%B8%82'
        # city_url = self.city_url.format(1, city_name)
        # yield scrapy.Request(url=city_url, headers=self.headers, meta={'city_name': city_name},  callback=self.city_to_shop)


    def city_to_shop(self,response):
        city_name = response.meta.get('city_name', '')
        page_num = response.meta.get('page_num', 1)
        json_data = json.loads(response.text)

        city_all_shop_nums = json_data.get('count', '')
        #解析店铺信息
        shop_list = json_data.get('datas', [])
        self.logger.info('开始抓取{}的店铺，第{}页，有{}家店铺'.format(city_name, page_num, len(shop_list)))
        for shop_item in shop_list:
            data_shop_item = MaidanglaoItem()
            data_shop_item.update(shop_item)
            yield data_shop_item


        all_page = int(int(city_all_shop_nums)/75) + 1
        for page_item in range(2, all_page + 1):
            req_url = self.city_url.format(str(page_item), city_name)
            yield scrapy.Request(url=req_url, headers=self.headers, meta={'city_name': city_name, 'page_num': page_item}, callback=self.city_to_shop)

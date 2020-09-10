# -*- coding: utf-8 -*-
import scrapy
import json
import requests
import time
from bigo_test.items import BigoTestItem

class BigoCeshiSpider(scrapy.Spider):

    name = 'bigo_ceshi'

    headers_0 = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'referer': 'http://www.bigo.tv/',

    }
    headers_1 = {
        'Host': 'www.bigolive.tv',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    headers_2 = {
        'Host': 'www.bigolive.tv',
        'Content-Length': '351',
        'Accept': '*/*',
        'Origin': 'http://www.bigolive.tv',
        'X-Requested-With': 'XMLHttpRequest',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.131 Safari/537.36',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive'
    }
    item = BigoTestItem()

    def start_requests(self):
        #category_url = 'http://www.bigolive.tv/openInterface/getGameCategory'   #获取分类
        #response = requests.get(url=category_url)
        #print(response.text)
        #data_list = json.loads(response.text)
        data_list = ['4Y', '1F', '10', '7C', '2l', '6G', '3k', '2g', '2J', '25', '1E', '2k', '5r', '69', '4k', '44', '4v', '5o', '57', '43', '4w', '4p', '4g', '5E', '2u', '27', '2s', '2i', '12', '3C', '6R', '29', '2B', '6T', '2M', '3o', '3i', '6p', '3a', '1S', '1p', '3D', '5u', '6W', '5M', '6d', '6m', '5p', '6K', '2v', '3E', '1M', '3r', '3y', '2r', '13', '5x', '5z', '2n', '6A', '6B', '6D', '2j', '2h', '6L', '6P', '2e', '23', '6V', '1Q', '6r', '16', '6k', '1H', '42', '3t', '3s', '47', '4N', '3m', '3j', '4o', '3g', '4t', '3d', '3c', '3T', '5C', '3O', '3H', '5N', '5W', '5d', '5i', '33', '1Z', '20']
        for data in data_list:
            link = 'http://www.bigolive.tv/openOfficialWeb/vedioList/11?tabType=' + str(data) + '&fetchNum=30'  # 获取分类下的tabId(tabId: "4R"),拼接url
            print(link)
            #self.logger.error("分类url:{}".format(link))
            yield scrapy.Request(url=link, meta={"tabId": data}, headers=self.headers_1, callback=self.parse)


    def parse(self, response):
        tabId = response.meta.get("tabId", "")
        #print(response.status_code)
        data_list_1 = json.loads(response.text)
        if data_list_1 is not None:
            post_data = ''
            post_page = 0
            for data_1 in data_list_1:
                detail_link = 'http://www.bigolive.tv/' + str(data_1['bigo_id'])   #获取贡献值的url
                # 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(data_json.get('extras', '').get('bigo_id', '')))
                detail_link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(data_1['bigo_id']))
                owner = str(data_1['owner']) + '.'
                post_data += owner
                post_data = post_data[0:-1]
                if len(data_list_1) == 30:   #判断需不需要翻页，翻页的话进行递归
                    post_page += 1
                    data_ = {
                        "ignoreUids": post_data,
                        "tabType": tabId
                    }
                    self.logger.error("当前区域为：{0}，页数为：{1}".format(tabId,str(post_page)))
                    url_1 = 'http://www.bigolive.tv/openOfficialWeb/vedioList/11'

                    yield scrapy.Request(url=url_1, method='post', headers=self.headers_2, body=json.dumps(data_), meta={"tabId": tabId}, callback=self.parse)

                yield scrapy.Request(url=detail_link, meta={'datas': data_1}, headers=self.headers_0, callback=self.parse_bean)

    def parse_bean(self, response):
        data_json = response.meta.get('datas','')
        batch = time.strftime('%Y-%m-%d %H') + ':00:00'    #
        data = json.loads(response.text)
        contribution_value = data.get('data', '').get('bean', '')

        extras = {}
        self.item['cat1'] = '游戏'
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
        extras['country'] = data_json['country']
        extras['country_name'] = data_json['country_name']
        self.item['extras'] = extras
        #
        yield self.item

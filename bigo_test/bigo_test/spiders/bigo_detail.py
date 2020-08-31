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
    today_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    bigo_id_item_set = '{}:{}_set'.format(base_key, today_time)    #去重是放在时间队列中去重
    bigo_id_item_list = '{}:item_list'.format(base_key)         #去重之后的都是放在一个整体的队列中
    no_liveing_key_set = '{}:nolive_set'.format(base_key)
    # ---------
    item = BigoTestItem()

    def start_requests(self):
        str_len = self.url_db.llen(self.bigo_id_item_list)
        if str_len > 0:
            for i in range(str_len):
                bigo_id_json = self.url_db.lpop(self.bigo_id_item_list)
                each = json.loads(bigo_id_json, encoding='utf-8')
                link = 'http://www.bigo.tv/' + str(each.get('extras', '').get('bigo_id', ''))
                yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)


    def parse(self, response):
        data_json = response.meta.get('datas', '')
        contribution_value = response.xpath('//i[@class="beans"]/text()').get()
        contry_area = response.xpath('//i[@class="country"]/text()').get()
        #print(type(data_json))
        if contribution_value == '0' and 'space' in contry_area:
            self.url_db.sadd(self.no_liveing_key_set, json.dumps(data_json))
            return

        data_json['contribution'] = contribution_value   #贡献值
        data_json['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))   #抓取时间
        self.item['cat1'] = '秀场'
        self.item['cat2'] = ''
        self.item.update(data_json)
        yield self.item


# -*- coding: utf-8 -*-
import scrapy
import json
import redis
import time

class CategoryListSpider(scrapy.Spider):
    name = 'category_list'
    # allowed_domains = ['163.com']
    # start_urls = ['http://163.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    }
    try:
        redis_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=1)
    except:
        redis_db = None
    base_key = 'swd_163'
    category_id_list_key = "{}:category_id_list".format(base_key)
    category_id_set_key = "{}:category_id_set".format(base_key)


    def start_requests(self):
        start_url = 'https://home.study.163.com/home/j/web/getFrontCategory.json'
        yield scrapy.Request(url=start_url, headers=self.headers)

    def parse(self, response):
        self.logger.debug(response.text)
        datas = json.loads(response.text)

        data = datas.get('result', [])
        for data_temp in data:
            parent_id = data_temp.get('id', '')  #----1-----
            if not self.redis_db.sismember(self.category_id_set_key, parent_id):
                self.redis_db.lpush(self.category_id_list_key, parent_id)
                self.redis_db.sadd(self.category_id_set_key, parent_id)

            children_list = data_temp.get('children', [])
            for children_temp in children_list:  #----2-----
                children_id = children_temp.get('id', '')
                if not self.redis_db.sismember(self.category_id_set_key, children_id):
                    self.redis_db.lpush(self.category_id_list_key, children_id)
                    self.redis_db.sadd(self.category_id_set_key, children_id)

                children_list0 = children_temp.get('children', [])    #----3-----
                for children_temp0 in children_list0:
                    children_id0 = children_temp0.get('id', '')
                    if not self.redis_db.sismember(self.category_id_set_key, children_id0):
                        self.redis_db.lpush(self.category_id_list_key, children_id0)
                        self.redis_db.sadd(self.category_id_set_key, children_id0)
        return

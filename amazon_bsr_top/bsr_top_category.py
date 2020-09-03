# coding:utf-8
import gevent
from gevent import monkey, pool
monkey.patch_all()
import sys
import traceback
import requests
import re
import time
import json
import copy
import datetime
from lxml import etree
import redis
import os

'''
通过对应分类，拼接bsrtop的url
格式化bsrtop的链接
'''
try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None

print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
base_url = 'https://www.amazon.com/Best-Sellers-{}/zgbs/{}/'
redis_dict_list = url_db.lrange('amazon_normal:all_category_list_bak', 0, -1)  #
for redis_dict in redis_dict_list:
    if isinstance(redis_dict, bytes):
        product_data = redis_dict.decode()
        product_data = json.loads(product_data)
        # print(product_data, type(product_data))
    dict_len = len(product_data.items())
    # print(dict_len, '===========')
    for num in range(2, int(dict_len / 2) + 1):
        temp = 'c{}'.format(str(num))
        temp_name = 'c{}_name'.format(str(num))
        cd = product_data.get(temp, '')
        cd_name = product_data.get(temp_name, '')
        # if ' & ' in cd_name or '' in cd_name or '' in cd_name or '' in cd_name or '' in cd_name
        cd_name = cd_name.replace(' & ', '-').replace(', ', '-').replace(' ', '-').replace('(', '').replace(')', '')

        cd_url = base_url.format(cd_name, cd)
        print(cd_url)
        if not url_db.sismember("amazon_category_bsrtop:urls_set", cd_url):
            url_db.sadd("amazon_category_bsrtop:urls_set", cd_url)
            url_db.lpush("amazon_category_bsrtop:urls_list", cd_url)
        cd_url2 = cd_url + '?&pg=2'
        print(cd_url2)
        if not url_db.sismember("amazon_category_bsrtop:urls_set", cd_url2):
            url_db.sadd("amazon_category_bsrtop:urls_set", cd_url2)
            url_db.lpush("amazon_category_bsrtop:urls_list", cd_url2)
print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))


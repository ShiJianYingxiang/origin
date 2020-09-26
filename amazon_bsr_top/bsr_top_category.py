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
2020-09-21: 添加URL，对应的分类信息
'''
try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None

print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
base_url = 'https://www.amazon.com/Best-Sellers-{}/zgbs/{}/'
redis_dict_list = url_db.lrange('amazon_category:info_list', 0, -1)  #

print(url_db.llen('amazon_category:info_list'))

for redis_dict in redis_dict_list:
    if isinstance(redis_dict, bytes):
        product_data = redis_dict.decode()
        url_db.sadd('amazon_category:info_set', product_data)  #
        product_data = json.loads(product_data)
        # print(product_data, type(product_data))

    dict_len = len(product_data.items())
    # print(dict_len, '===========')
    for num in range(2, int(dict_len / 2) + 1):
        data = {}
        temp = 'c{}'.format(str(num))
        temp_name = 'c{}_name'.format(str(num))
        cd = product_data.get(temp, '')
        cd_name = product_data.get(temp_name, '')
        # if ' & ' in cd_name or '' in cd_name or '' in cd_name or '' in cd_name or '' in cd_name
        cd_name = cd_name.replace(' & ', '-').replace(', ', '-').replace(' ', '-').replace('(', '').replace(')', '')
        cd_url = base_url.format(cd_name, cd)
        data['url_1'] = cd_url
        data['url_2'] = cd_url + '?&pg=2'
    data['category'] = product_data
    print('----{}----'.format(data))
    if not url_db.sismember("amazon_category_bsrtop:urls_set", json.dumps(data)):
        url_db.sadd("amazon_category_bsrtop:urls_set", json.dumps(data))
        url_db.lpush("amazon_category_bsrtop:urls_list", json.dumps(data))
print('END_time:{}---{}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), url_db.llen("amazon_category_bsrtop:urls_list")))


# -*- coding: utf-8 -*-
# @Time    : 2020/9/15 13:51
# @Author  : swd
# @fun     :采集多个sku对应的评论数
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

monkey.patch_all()
exe_pool = pool.Pool(60)

redishandler = redis.Redis(host='172.21.15.57', port=6379, db=12)
PROXY_KEY = "pycrawler_proxies:dly"
# PROXY_KEY = "pycrawler_proxies:foreign"   #博文海外代理
try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None


def download(url, product_data):
    product_id = product_data.get('pid', '')
    resp = None
    success = False
    exe_cnt = 0
    while not success and exe_cnt < 10:
        try:
            exe_cnt += 1
            proxy = redishandler.srandmember(PROXY_KEY)
            # srandmember
            if isinstance(proxy, bytes):
                proxy = proxy.decode()
            proxies = {
                "http": "http://databurning:2tQJl*t8@{}".format(proxy),
                "https": "https://databurning:2tQJl*t8@{}".format(proxy)
                #---------海外代理---------
                # "http": "http://databurning:databurning@{}".format(proxy),
                # "https": "https://databurning:databurning@{}".format(proxy),
            }
            print('proxies is ---------', proxies)
            headers = {
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
            }
            cookies = {
                # 'session-id': '143-0582700-9583307',   #144-5953255-9071136
                'session-id': '144-9518903-4476439',   #144-5953255-9071136
                # 'ubid-main': '133-1649099-9448018',     #133-0153621-7443973
                'ubid-main': '130-0947211-4141062',     #133-0153621-7443973
                'i18n-prefs': 'USD',    #i18n-prefs=USD
            }
            data = {
                'sortBy': '',
                'reviewerType': 'all_reviews',
                'formatType': 'current_format',
                'mediaType': '',
                'filterByStar': '',
                'pageNumber': '1',
                'filterByLanguage': '',
                'filterByKeyword': '',
                'shouldAppend': 'undefined',
                'deviceType': 'desktop',
                'canShowIntHeader': 'undefined',
                'reftag': 'cm_cr_arp_d_viewopt_fmt',
                'pageSize': '10',
                # 'asin': product_id,
                'asin': 'B07C812LHQ',
                # B003LTDYDM
                'scope': 'reviewsAjax0',
            }
            resp = requests.post(url, timeout=5, proxies=proxies, headers=headers, verify=False, data=data)  #, cookies=cookies
            if 'Robot Check' in resp.text:
                print('Robot Check===={}==='.format(exe_cnt))
                success = False
            else:
                success = True
        except:
            if exe_cnt == 10:
                # url_db.sadd(swd_amazon_product_set, url)   #????????????????????
                print('10次都出现Robot Check======={}=========='.format(url))
                # url_db.lpush("amazon_normal:failed_category_url", url)
    if success:
        return resp
    else:
        print('10次抓取都失败====={}=========='.format(url))
        if not url_db.sismember('amazon_comments:failed_set', json.dumps(product_data)):
            url_db.sadd('amazon_comments:failed_set', json.dumps(product_data))
            url_db.lpush("amazon_comments:failed_list", json.dumps(product_data))


def parse_list(url, product_data):
    content_dict = {}
    resp = download(url, product_data)
    # 467 global ratings | 253 global reviews
    # print('正在抓取---{}---'.format(product_id))
    # print(resp.text)
    pid = product_data.get('pid', '')
    batch_tm = product_data.get('batch_time', '')

    try:
        comments_num = re.search(r'(\d+)\s*global\s*rating', resp.text).group(1)
    except:
        comments_num = ''
        if not url_db.sismember('amazon_comments:no_comment_set', json.dumps(product_data)):
            url_db.sadd('amazon_comments:no_comment_set', json.dumps(product_data))
            url_db.lpush("amazon_comments:no_comment_list", json.dumps(product_data))

    comments_num = comments_num.replace(',', '').strip()
    content_dict['pid'] = pid
    content_dict['batch_tm'] = batch_tm
    content_dict['comments_num'] = comments_num

    # print(content_dict)
    with open('/mnt/data/weidong.shi/file/amazon/sku_to_comment/' + time.strftime('%Y-%m-%d') + '_' + str(os.getpid()) + '.txt', 'a+', encoding='utf-8') as ff:
    #with open(time.strftime('%Y-%m-%d') + '_' + str(os.getpid()) + '.txt', 'a+', encoding='utf-8') as ff:
        ff.write(json.dumps(content_dict) + '\n')

def get_data():
    job = []
    print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    while 1:
        redis_dict = url_db.lpop('amazon_comments:start_list')  #
        if redis_dict:
            if isinstance(redis_dict, bytes):
                product_data = redis_dict.decode()
                product_data = json.loads(product_data.replace('\'', '\"'))
                product_url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_fmt'
                # print(product_url)
                job.append(exe_pool.spawn(parse_list, product_url, product_data))
        else:
            print('队列已消耗完毕，退出')
            break
    ################################
    #product_id = 'B07C812LHQ'

    #product_url = 'https://www.amazon.com/hz/reviews-render/ajax/reviews/get/ref=cm_cr_arp_d_viewopt_fmt'
    # print(product_url)
    #job.append(exe_pool.spawn(parse_list, product_url, product_id))


    # B088FDVJG4
    # product_list = ['B08C5ZVN95', 'B07YNKTF6H', 'B07YNJ4X2P', 'B07VM866DV', 'B086QRVL8P', 'B089Y3R1V9', 'B07YNLYYNK', 'B07Z3WF3NG', 'B07VFWRVPS', 'B088VXKSN9']   #B088FDVJG4没有bsr
    # for product_id in product_list:
    #
    #     product_url = 'https://www.amazon.com/dp/{}/'.format(product_id)
    #     job.append(exe_pool.spawn(parse_list, product_url))
    # B088FDVJG4
    # product_id = 'B088FDVJG4'
    # product_list = ['B08C5ZVN95', 'B07YNKTF6H', 'B07YNJ4X2P', 'B07VM866DV', 'B086QRVL8P', 'B089Y3R1V9', 'B07YNLYYNK', 'B07Z3WF3NG', 'B07VFWRVPS', 'B088VXKSN9']   #B088FDVJG4没有bsr
    # for product_id in product_list:
    # redis_dict = url_db.lpop('amazon_import:detail_list')  #
    # if redis_dict:
    #     if isinstance(redis_dict, bytes):
    #         product_data = redis_dict.decode()
    #         product_data = json.loads(product_data.replace('\'', '\"'))
    #         product_id = product_data.get('pid', '')
    #         product_url = 'https://www.amazon.com/dp/{}'.format(product_id)
    #         print(product_url)
    #         job.append(exe_pool.spawn(parse_list, product_url, product_data))
    # else:
    #     print('队列已消耗完毕，退出')
        # break
    # product_url = 'https://www.amazon.com/dp/{}'.format(product_id)
    # job.append(exe_pool.spawn(parse_list, product_url))

    gevent.joinall(job)
    print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))


if __name__ == '__main__':
    get_data()




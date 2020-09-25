# -*- coding: utf-8 -*-
# @Time    : 2020/9/23 13:53
# @Author  : swd
# @fun     :通过品牌关键词搜索对应的category分类，获取品牌ID
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
通过对应品牌下的一级分类，获取翻页数，进行翻页并获取每页下的商品ID---效果不好---(半个月一次)
'''

exe_pool = pool.Pool(10)

try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None

redishandler = redis.Redis(host='172.21.15.57', port=6379, db=12)
PROXY_KEY = "pycrawler_proxies:dly"


def download(url):
    resp = None
    success = False
    exe_cnt = 0
    while not success and exe_cnt < 10:
        try:
            exe_cnt += 1
            proxy = redishandler.srandmember(PROXY_KEY)
            if isinstance(proxy, bytes):
                proxy = proxy.decode()
            proxies = {
                "http": "http://databurning:2tQJl*t8@{}".format(proxy),
                "https": "https://databurning:2tQJl*t8@{}".format(proxy)
            }
            print('proxies is ---------', proxies)
            headers = {
                "accept": "application/json, text/javascript, */*; q=0.01",
                "accept-encoding": "gzip, deflate, br",
                "accept-language": "zh-CN,zh;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "pragma": "no-cache",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
                "x-requested-with": "XMLHttpRequest",
            }
            cookies = {
                # 'session-id': '143-0582700-9583307',   #144-5953255-9071136
                'session-id': '137-1388175-2163751',   #144-5953255-9071136
                # 'ubid-main': '133-1649099-9448018',     #133-0153621-7443973
                'ubid-main': '132-8752816-7169523',     #133-0153621-7443973
                'i18n-prefs': 'USD',    #i18n-prefs=USD
            }
            resp = requests.get(url, timeout=5, proxies=proxies, cookies=cookies, headers=headers,
                                verify=False)  # , cookies=cookies
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
        if not url_db.sismember('amazon_brand:failed_urls_set', url):
            url_db.sadd('amazon_brand:failed_urls_set', url)
            url_db.lpush("amazon_brand:failed_urls_list", url)

    # --------------java接口请求-----------------------------
    # try:
    #     cookies_content = url_db.srandmember('amazon_detail_spider:cookies_set')
    #     if isinstance(cookies_content, bytes):
    #         cookies_content = cookies_content.decode()
    #     cookies_content = json.loads(cookies_content)
    #     time_stamp = str(int(time.time()*1000))
    #     headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "pragma": "no-cache","sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin","user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36","cookies": 'session-id=' + str(cookies_content.get('session_id', ''))+';ubid-main=' + str(cookies_content.get('ubid_main', ''))+';i18n-prefs=USD;csm-hit=tb:ddddKP9AEMV9PF10XHG4+s-7YR2KP9AEMV9PF10XHG4|'+time_stamp+'&t:'+time_stamp+'&adb:adblk_no;session-token=kRH+cLX+JLmd0T5vC/UW0GmRwwp/KN6OU6E/iWxRzkVnLCzi+24+Ny1QyYKl1GFDCcdc3s2gOQn0+222220xm4aKSipEzNjfUxn12c7xJNIJsyUcWIBITYEhwrKyJaWCgyjQbjMfgVlqtLns3HD8+d/tpVfoo/J6ioZhvKW4DrPtKgCjw92qW0GUzW5ZlGxl;x-wl-uid=15/lJL6ZuCc88bu2UNMVdyUmWE1hS64Bo0NVs4QZXKH2jFMh+0rtV333KutuXXNTQrmD+r3yFfrc='}
    #     payload = {
    #         "url": url,
    #         "headers": headers,
    #     }
    #     # web_url = "http://172.21.15.74:8092/asdfa"
    #     #web_url = "http://172.19.228.108:8092/asdfa"
    #     web_url = "http://172.21.15.66:8092/asdfa"
    #     # web_url = "http://10.2.103.63:8092/asdfa"
    #     web_headers = {
    #         'Content-Type': 'text/plain'
    #     }
    #     datas = json.dumps(payload)
    #     response = requests.request("POST", web_url, headers=web_headers, data=datas)
    #     return response
    # except Exception as msg:
    #     print(msg)
    #     # print('========ID:{0}==========>error:{1}==='.format(pid, msg))
    #     # if not url_db.sismember('amazon_detail_spider:failed_urls_set', pid):
    #     #     url_db.sadd('amazon_detail_spider:failed_urls_set', pid)
    #     #     url_db.lpush("amazon_detail_spider:failed_urls_list", pid)

def parse_category(url, barnd_name):
    # 获取一级分类的链接
    resp = download(url)
    response = etree.HTML(resp.text)
    brand_top_category = response.xpath('''//div[@id="departments"]//ul//li[@class="a-spacing-micro"]//a/@href''')
    category_url_list = []
    for category_item in brand_top_category:
        if barnd_name not in category_item:  #anker
            continue
        if 'instant-video' in category_item:
            continue
        if 'i=toys-and-games' in category_item:
            continue
        if 'i=industrial' in category_item:
            continue
        if '&ref=' in category_item:
            category_item = category_item.split('&ref=')[0]
        category_url = 'https://www.amazon.com' + category_item
        category_url_list.append(category_url)
    return category_url_list

def parse_list(url):
    # 解析每个分类下的总页数，翻页并拼接链接
    resp = download(url)
    response = etree.HTML(resp.text)
    page_nums = []
    try:
        country = response.xpath('''(//div[@id="glow-ingress-block"]//span)[2]/text()''')[0]
        country = country.replace('\n', '').replace(' ', '')
    except:
        pass
    try:
        total_page_number = response.xpath('''(//ul[@class="a-pagination"]//li)[last()-1]/text()|(//ul[@class="a-pagination"]//li)[last()-1]/a/text()''')[0]  # 获取总的页数
        if total_page_number:
            print('=======该链接下{}====总页数是{}========='.format(url, total_page_number))
            for item in range(1, int(total_page_number) + 1):
                next_page_url = url + '&page=' + str(item)
                page_nums.append(next_page_url)
    except:
        page_nums.append(url)
    # print(len(page_nums), '======page_nums========')
    return page_nums


def parse_page_detail(url):
    # 解析每页下的商品，获取商品ID
    resp = download(url)
    search_key = re.search('k=(\w+)&', url).group(1)
    # print('======{}===={}===='.format(url, search_key))

    response = etree.HTML(resp.text)
    bt_time = time.strftime('%Y-%m-%d')
    try:
        country = response.xpath('''(//div[@id="glow-ingress-block"]//span)[2]/text()''')[0]
        country = country.replace('\n', '').replace(' ', '')
        print('====This is {}=========='.format(country))
    except:
        pass

    try:
        productid_list = response.xpath(
            '''//div[@class="a-section a-spacing-medium"]//h2//a/@href|//div[@id="anonCarousel1"]//h2//a//@href''')
    except:
        print('解析详情出错----{}----'.format(url))
        # if not url_db.sismember('amazon_brand:failed_urls_set', url):
        #     url_db.sadd('amazon_brand:failed_urls_set', url)
        #     url_db.lpush("amazon_brand:failed_urls_list", url)
        return

    now_page_productid_num = str(len(productid_list))

    if productid_list:
        print('-----链接:{}---展示商品量为{}--------'.format(url, now_page_productid_num))
    else:
        print('-----链接:{}---无展示商品--------'.format(url))

    for product_temp in productid_list:
        productID = re.findall(r'dp/(\w{10})/', product_temp)
        if productID:
            productID = productID[0]
            if isinstance(productID, int):
                continue
            # product_info = {}
            # product_info['pid'] = productID
            # product_info['bt_time'] = bt_time
            # # product_info['search'] = 'key'
            # print(product_info)
            # if not url_db.sismember("amazon_brand:{}_product_set".format(search_key), json.dumps(product_info)):
            #     url_db.sadd("amazon_brand:{}_product_set".format(search_key), json.dumps(product_info))
            #     url_db.lpush("amazon_brand:{}_product_list".format(search_key), json.dumps(product_info))
            if not url_db.sismember("amazon_brand:{}_product_set".format(search_key), productID):
                url_db.sadd("amazon_brand:{}_product_set".format(search_key), productID)
                url_db.lpush("amazon_brand:{}_product_list".format(search_key), productID)

def get_data():
    job = []
    # **************通过品牌关键词搜索出一级类的链接进行扩展**************************
    print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    barnd_name_list = ['anker', 'aukey'] #, 'anker'

    for barnd_name in barnd_name_list:
        # https://www.amazon.com/s?k=anker
        search_key_url = 'https://www.amazon.com/s?k={}'.format(barnd_name)
        job.append(exe_pool.spawn(parse_category, search_key_url, barnd_name))
        gevent.joinall(job)

        category_nums_job = []    #
        for i, g in enumerate(job):    #循环获取品牌下的一级分类链接，并获取对应的页数进行翻页拼接url
            for page_url in g.value:
                # print(page_url, '---------------@@@@@@@@@@@-----------')
                page_url = page_url #+ '&qid={}'.format(str(int(time.time())))
                category_nums_job.append(exe_pool.spawn(parse_list, page_url))
        gevent.joinall(category_nums_job)

        detail_job = []
        for i, g in enumerate(category_nums_job):    #循环获取每一页的链接
            if not g:
                continue
            for detail_url in g.value:
                if not detail_url:
                    continue
                if 'i=toys-and-games' in detail_url:
                    continue
                if 'i=industrial' in detail_url:
                    continue
                detail_job.append(exe_pool.spawn(parse_page_detail, detail_url))
        gevent.joinall(detail_job)


    print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))



if __name__ == '__main__':
    get_data()






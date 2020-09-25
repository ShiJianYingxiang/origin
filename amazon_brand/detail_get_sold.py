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
通过关键词和分类搜索出的商品ID，进行解析获取Sold by(商铺)
'''
exe_pool = pool.Pool(20)

try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None

redishandler = redis.Redis(host='172.21.15.57', port=6379, db=12)
PROXY_KEY = "pycrawler_proxies:dly"


def download(url):
    productID = re.findall(r'/(\w{10})', url)
    pid = productID[0] if productID else None  # 商品唯一标识
    if not pid:
        print('传递的链接有错误')
        return

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
        if not url_db.sismember('amazon_brand:failed_market_urls_set', url):
            url_db.sadd('amazon_brand:failed_market_urls_set', url)
            url_db.lpush("amazon_brand:failed_market_urls_list", url)
    # ******************************************
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

def parse_list(url, brand_name):
    resp = download(url)

    productID = re.findall(r'/(\w{10})', url)
    pid = productID[0] if productID else None  # 商品唯一标识
    if not pid:
        print('没有找到商品ID')
    print('---{}---开始抓取merchantid----{}---'.format(time.strftime('%Y-%m-%d %H:%M:%S'), pid))
    # if not resp:
    #     if not url_db.sismember('amazon_search_spider:aukey_error_set', pid):
    #         url_db.sadd('amazon_search_spider:aukey_error_set', pid)
    #         url_db.lpush("amazon_search_spider:aukey_error_list", pid)
    #     print('*********error********返回无数据*******************')
    #     return

    response = etree.HTML(resp.text)

    # 标题
    title_content = response.xpath('''//h1//span[@id="productTitle"]/text()''')[0]
    title_content1 = title_content.replace('\n', '').replace('Amazon.com: ', '').replace('Amazon.com : ', '')
    try:
        title = title_content1.split(':')[0].strip()
    except:
        title = title_content1.strip()
    if brand_name not in title.lower():  #品牌名称不在标题中，返回不取店铺ID
        return

    # 地区
    try:
        country = response.xpath('''(//div[@id="glow-ingress-block"]//span)[2]/text()''')[0]
        country = country.replace('\n', '').replace(' ', '')
        print('====This is {}=========='.format(country))
    except:
        pass

    #获取商品对应的店铺ID
    marketplace_content = dict()
    try:
        me = response.xpath('''//input[@id="merchantID"]//@value|//input[@id="usedMerchantID"]//@value''')[0]
        if me:
            me = me
            marketplaceID = re.search(r'marketplaceId\s*[\'\"]\s*[:：]\s*[\'\"]\s*(.*?)\s*[\'\"]\s*', resp.text).group(1)
            marketplace_content['me'] = me
            marketplace_content['marketplaceID'] = marketplaceID
    except:
        me = ''
        marketplaceID = ''
        print('----该商品没有Sold by榜单-------')
        marketplace_content['me'] = me
        marketplace_content['marketplaceID'] = marketplaceID

    print(marketplace_content, '-----------------------')
    if not url_db.sismember("amazon_brand:{}_market_set".format(brand_name), json.dumps(marketplace_content)):
        url_db.sadd("amazon_brand:{}_market_set".format(brand_name), json.dumps(marketplace_content))
        url_db.lpush("amazon_brand:{}_market_list".format(brand_name), json.dumps(marketplace_content))


def get_data():
    job = []
    # ----------******通过商品ID获取里面的品牌店铺-----------------------
    print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

    brand_name_list = ['anker', 'aukey']
    for brand_name in brand_name_list:
        product_list = url_db.lrange("amazon_brand:{}_product_list".format(brand_name), 0, -1)
        for product_ID in product_list:
            if isinstance(product_ID, bytes):
                product_ID = product_ID.decode()
                product_data = json.loads(product_ID)
                product_ID = product_data.get('pid', '')
            product_url = 'https://www.amazon.com/dp/{}/'.format(product_ID)
            job.append(exe_pool.spawn(parse_list, product_url, brand_name))
        gevent.joinall(job)

    print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

    # ------------对错误队列进行重试--------------------
    # print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    # while 1:
    #     redis_dict = url_db.lpop('amazon_search_spider:error_list')   #
    #     if redis_dict:
    #         if isinstance(redis_dict, bytes):
    #             product_id = redis_dict.decode()
    #             product_url = 'https://www.amazon.com/dp/{}/'.format(product_id)
    #             job.append(exe_pool.spawn(parse_list, product_url))
    #     else:
    #         print('队列已消耗完毕，退出')
    #         break
    # gevent.joinall(job)
    # print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))


if __name__ == '__main__':
    get_data()

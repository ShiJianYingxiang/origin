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
import codecs
import datetime
from lxml import etree
import redis
import os
'''
1.解析每个榜单链接的信息
2.并将获取的商品id进行保存

'''
monkey.patch_all()
exe_pool = pool.Pool(100)

redishandler = redis.Redis(host='172.21.15.57', port=6379, db=12)
PROXY_KEY = "pycrawler_proxies:dly"
try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None


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
                'session-id': '144-5953255-9071136',   #144-5953255-9071136
                # 'ubid-main': '133-1649099-9448018',     #133-0153621-7443973
                'ubid-main': '133-0153621-7443973',     #133-0153621-7443973
                'i18n-prefs': 'USD',    #i18n-prefs=USD
            }
            resp = requests.get(url, timeout=5, proxies=proxies, cookies=cookies, headers=headers, verify=False)  #, cookies=cookies
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
        if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', url):
            url_db.sadd('amazon_category_bsrtop:failed_urls_set', url)
            url_db.lpush("amazon_category_bsrtop:failed_urls_list", url)

def clear_special_xp(data, xp):
    data = copy.copy(data)
    result = data.xpath(xp)
    for i in result:
        try:
            i.getparent().remove(i)
        except Exception as e:
            print(e)
    return data


def parse_list(url):
    resp = download(url)

    bt_time = time.strftime('%Y-%m-%d')
    categoryid = re.search('zgbs/(.*?)/', url).group(1)

    try:
        content = etree.HTML(resp.text)
        content = clear_special_xp(content, '//style|//script')  # 去除杂质
    except:
        if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', url):
            url_db.sadd('amazon_category_bsrtop:failed_urls_set', url)
            url_db.lpush("amazon_category_bsrtop:failed_urls_list", url)
        return
#   解析列表的信息  |
    bsr_top_name = content.xpath('''//div[@id="zg"]//h1/text()''')[0] + content.xpath('''//div[@id="zg"]//h1//span/text()''')[0]  # bsr_top的名称

    bsr_list_info = content.xpath('''//ol[@id="zg-ordered-list"]//li''')

    print('---{}正在抓取{},显示个数是{}---'.format(time.strftime('%Y-%m-%d %H:%M:%S'), url, len(bsr_list_info)))
    # if len(bsr_list_info) != 50:
    #     if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', url):
    #         url_db.sadd('amazon_category_bsrtop:failed_urls_set', url)
    #         url_db.lpush("amazon_category_bsrtop:failed_urls_list", url)

    for bsr_item in bsr_list_info:
        bsr_top_rank = dict()
        bsr_rank = bsr_item.xpath('''.//span[@class="zg-badge-text"]/text()''')[0]  #bsr排名
        if bsr_rank:
            bsr_rank = bsr_rank.replace('#', '').strip()
        # //ol[@id="zg-ordered-list"]//li//div[contains(@class,"p13n-sc-truncate")]
        bsr_produce_title = bsr_item.xpath('''.//div[contains(@class,"p13n-sc-truncate")]/text()''')[0].strip() #对应的商品title

        # //ol[@id="zg-ordered-list"]//li//span[@class="aok-inline-block zg-item"]/a[@class="a-link-normal"]---对应链接
        bsr_produce_id_temp = bsr_item.xpath('''.//span[@class="aok-inline-block zg-item"]/a[1]/@href''')[0] #对应的商品id
        bsr_produce_id = re.findall(r'dp/(\w{10})', bsr_produce_id_temp)
        bsr_produce_id = bsr_produce_id[0] if bsr_produce_id else None  # 商品唯一标识

        try:
            # //ol[@id="zg-ordered-list"]//li//span[@class="p13n-sc-price"]
            bsr_produce_price = bsr_item.xpath('''.//span[@class="p13n-sc-price"]/text()''')[0] #对应的商品价格
            if bsr_produce_price:
                bsr_produce_price = bsr_produce_price.replace('$', '').strip()
        except:
            bsr_produce_price = ''

        try:
            #//ol[@id="zg-ordered-list"]//li//div[@class="a-icon-row a-spacing-none"]/a[last()]
            bsr_produce_comments = bsr_item.xpath('''.//div[@class="a-icon-row a-spacing-none"]/a[last()]/text()''')[0] #对应的商品评论数
            if bsr_produce_comments:
                bsr_produce_comments = bsr_produce_comments.replace(',', '').strip()
        except:
            bsr_produce_comments = ''

        try:
            #//ol[@id="zg-ordered-list"]//li//div[@class="a-icon-row a-spacing-none"]/a/@title
            bsr_produce_comments_content = bsr_item.xpath('''.//div[@class="a-icon-row a-spacing-none"]//span/text()''')[0] #对应的商品评论星级
            if bsr_produce_comments_content:
                if 'out' in bsr_produce_comments_content:
                    bsr_produce_comments_content = bsr_produce_comments_content.split('out')[0].strip()
        except:
            bsr_produce_comments_content = ''

        # 保存为bsrtop_list_info
        bsr_top_rank['bsr_top_name'] = bsr_top_name             #bsr_top的名称
        bsr_top_rank['bsr_rank'] = bsr_rank                     #bsr排名
        bsr_top_rank['bsr_produce_title'] = bsr_produce_title   #对应的商品title
        bsr_top_rank['bsr_produce_id'] = bsr_produce_id         #对应的商品id
        bsr_top_rank['bsr_produce_price'] = bsr_produce_price   #对应的商品价格
        bsr_top_rank['bsr_produce_comments'] = bsr_produce_comments   #对应的商品评论数
        bsr_top_rank['bsr_produce_comments_content'] = bsr_produce_comments_content  #对应的商品评论星级
        bsr_top_rank['category_id'] = categoryid  #对应的商品评论星级
        bsr_top_rank['bt_time'] = bt_time
        bsr_top_rank['crawler_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 采集时间

        with open('/mnt/data/weidong.shi/file/amazon/bsrtop_rank/bsrtop_list_info_' + time.strftime('%Y-%m-%d') + '.txt', 'a+', encoding="utf-8") as file:
            file.write(json.dumps(bsr_top_rank) + '\n')

        #将商品id存储在redis中
        product_info = {}
        product_info['pid'] = bsr_produce_id
        product_info['batch_time'] = bt_time
        product_info['source'] = 'bsr_parse'
        if not url_db.sismember('amazon_category_bsrtop:produce_id_set', json.dumps(product_info)):
            url_db.sadd('amazon_category_bsrtop:produce_id_set', json.dumps(product_info))
            url_db.lpush("amazon_category_bsrtop:produce_id_list", json.dumps(product_info))


def get_data():
    job = []
    print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    redis_dict_list = url_db.lrange('amazon_category_bsrtop:urls_list', 0, -1)  #
    for redis_dict in redis_dict_list:
        if isinstance(redis_dict, bytes):
            bsr_top_url = redis_dict.decode()
            job.append(exe_pool.spawn(parse_list, bsr_top_url))
    gevent.joinall(job)


    #失败队列重试
    # while 1:
    #     redis_dict = url_db.lpop('amazon_category_bsrtop:urls_list1')   #
    #     if redis_dict:
    #         if isinstance(redis_dict, bytes):
    #             bsr_top_url = redis_dict.decode()
    #             job.append(exe_pool.spawn(parse_list, bsr_top_url))
    #     else:
    #         print('队列已消耗完毕，退出')
    #         break

    print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))

if __name__ == '__main__':
    get_data()

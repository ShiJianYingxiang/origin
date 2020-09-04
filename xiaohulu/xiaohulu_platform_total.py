# coding:utf-8
import requests
import json
import pymongo
import re
import time
import datetime
import traceback
import logging
import gevent
import redis
from gevent import monkey, pool
import sys
# reload(sys)
# sys.setdefaultencoding('utf8')
import warnings
warnings.filterwarnings('ignore')
'''
小葫芦获取平台榜单数据
'''

client = pymongo.MongoClient(host='mongodb://spider:spidermining@172.20.207.10:27051,172.20.207.12:27051,172.20.207.13:27051/admin',document_class=dict, tz_aware=True)
db = client.spider_invs

monkey.patch_all()
exe_pool = pool.Pool(1)
redishandler = redis.Redis(host='172.21.15.64', port=6379, db=15)
#batch = (datetime.datetime.now() + datetime.timedelta(days=-1)).strftime("%Y-%m-%d")
PROXY_KEY = "pycrawler_proxies:dly"

try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=13)
except:
    url_db = None



def download(url, link_id, date_time):
    print(url, link_id, date_time)
    resp = None
    success = False
    exe_cnt = 0
    while not success and exe_cnt < 3:
        try:
            exe_cnt += 1
            headers = {
                'content-length': '18',
                'accept': 'application/json, text/plain, */*',
                'origin': 'https://www.xiaohulu.com',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36',
                'token': '8ce8a99be3612461204543fbda3ec071',
                'content-type': 'application/json;charset=UTF-8',
                'sec-fetch-site': 'same-origin',
                'sec-fetch-mode': 'cors',
                'referer': 'https://www.xiaohulu.com/stryPlatform',
                'accept-encoding': 'gzip, deflate, br',
                'accept-language': 'zh-CN,zh;q=0.9',
                # 'cookie': 'xhl_cok=11a0%2FEzL0eP5SloxLmqAnNswMxDAuX4cR5BirTRnA%2BrdbH5JvgkLPwNm5yklUQdd5IfN11IYNRZo6ksqhw; Hm_lvt_1c358b33dfa30c89dd3a1927a5921793=1597629757,1598184492,1598842758,1598926287; xhl_pc_token=14e782ecd9365ff8e3e2588f8d8a0343; Hm_lpvt_1c358b33dfa30c89dd3a1927a5921793=1599031665; www_session=eyJpdiI6IjFDdThMUjlJZUtXTVAycDFaZERDK2c9PSIsInZhbHVlIjoiSkxqXC9peGVHU0NKZWZHcVwvOVNPNUxTQTNkZ1FyXC9EZ1BcL0w3a21ZMVZnMSt0dWNPMUNKOUlqYTUzUUVjakNLRFIiLCJtYWMiOiI3ZTcyODNjMmFmZmRlNTVkOGU5ZmYzMGFiYWY2NzdhZGQ4OTczZTgwNGQ2YzY0ZjJmYWZhMDM4MGQ1ZGMwODY4In0%3D',
            }
            param = {
                "flag": "platform_rank",
	            "order_key": "",
	            "page": 1,
	            "pagesize": 100,
	            "filter": {
		        "time_type": "day",
		        "start_time": date_time
	            }
            }
            proxy = redishandler.srandmember(PROXY_KEY)
            proxy = "http://databurning:2tQJl*t8@{}".format(proxy)
            proxies = {"https": proxy}
            param = json.dumps(param)
            token = url_db.hget('xiaohulu_token', 'token')
            if isinstance(token, bytes):
                token = token.decode()
            headers.update({'token': token})  #更新token
            resp = requests.post(url, headers=headers, data=param, timeout=10, verify=False)

            jo = json.loads(resp.text)
            if jo['code'] != 0:
                success = False
            else:
                success = True
        except:
            if exe_cnt == 3:
                print('下载错误:%s' % url)
                print(traceback.format_exc())

    if success:
        return resp
    else:
        print('3次抓取都失败')

def parse_list(link):
    time.sleep(3)
    # date_time = '2020-09-' + link_id   #link_id 是天数
    date_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    link_id = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%d')
    print('---{}开始抓取{}的榜单数据----------'.format(time.strftime('%Y-%m-%d %H:%M:%S'), date_time))
    resp = download(link, link_id, date_time)
    #print(resp.text)
    data_list = json.loads(resp.text)
    for data in data_list['data']['data']:
        item = {}
        item['platform_name'] = data['platform_name']
        item['gift_income'] = data['show_value']
        item['active_anchor_num'] = data['anchor_live_num']
        item['gift_sender_num'] = data['gift_sender_num']
        item['danmaku_num'] = data['danmaku_num']
        item['batch'] = date_time
        item['danmaku_sender_num'] = data['danmaku_sender_num']
        print('--{}----->{}'.format(date_time, item))
        db['xiaohulu_platform_total'].save(item)
def get_data():
    job = []
    link = 'https://www.xiaohulu.com/apis/bd/anchor/anchor/index'
    job.append(exe_pool.spawn(parse_list, link))
    gevent.joinall(job)

if __name__ == '__main__':
    get_data()


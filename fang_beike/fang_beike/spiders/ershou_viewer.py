# -*- coding: utf-8 -*-
import scrapy
import requests
import json
import re
import time
from urllib import parse
import hashlib
import base64
import redis
from fang_beike.items import FangBeikeErShouViewerItem





class ErshouViewerSpider(scrapy.Spider):
    name = 'ershou_viewer'
    custom_settings = {
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': './././Log/scrapy_{}_{}.log'.format('ershou_viewer', time.strftime('%Y-%m-%d'))
    }
    format_url = 'https://app.api.ke.com/house/house/seeRecordV2?house_code={}&city_id=&limit_count=20&limit_offset={}'
    ori_headers = {
        'x-req-id': '69ddfab3-e565-4c57-9b83-5e1e39f49329',
        'Page-Schema': 'rentalHouse%2Fdetail%2Frecord',
        'Referer': 'ershou%2Fdetail',
        'Cookie': 'lianjia_udid=861322030797829;lianjia_ssid=cf0b7d4f-eb1a-4641-a97e-0fe6c4399d58;lianjia_uuid=345eab00-91c3-4de7-8317-3b1aeb972fb8',
        'source-global': '{}',
        'User-Agent': 'Beike2.39.0;Xiaomi MI+5; Android 6.0.1',
        'Lianjia-Channel': 'Android_ke_sm_zu_dy_ty_12_wai_zhitou',
        'Lianjia-Device-Id': '861322030797829',
        'Lianjia-Version': '2.39.0',
        'Lianjia-Im-Version': '2.34.0',
        'Lianjia-Recommend-Allowable': '1',
        'extension': 'lj_imei=861322030797829&lj_duid=DuGmaBC3rNBWAoWOPjZrbXZapgmiL9opFFTNqU+nuEegz7Yb6i2cOkI1aGTOlHuqe/fOQXdmm0y+qrfe0LcRmDAA&lj_android_id=de32b13ef90e84f4&lj_device_id_android=861322030797829&mac_id=B0:E2:35:22:2D:09',
        'Host': 'app.api.ke.com',
    }
    try:
        # url_db = redis.StrictRedis(host='112.126.102.89', port=6379, db=7, password='dalian')
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None

    batch_time = '2020-08-31'#time.strftime('%Y-%m-%d')



    def dingding(self, msg):
        try:
            url = 'https://oapi.dingtalk.com/robot/send?access_token=97408fc11ab3eb232898ed6c8f81567996aa81c0460ca655aba1fc8c7ecfa334'
            headers = {"Content-Type": "application/json"}
            data = json.dumps({
                "msgtype": "text",
                "text": {
                    "content": msg,
                         }
            })
            response = requests.post(url, data=data, headers=headers, verify=False)
            # requests.get(url)
        except Exception as error:
            return "dingding_report error，{}，{}".format(msg, error)



    def auth(self, query):
        res = dict(parse.parse_qsl(query, keep_blank_values=True))
        res = sorted(res.items(), key=lambda d: d[0], reverse=False)
        x = ''
        for r in res:
            x = x + r[0] + '=' + r[1]
        x = 'd5e343d453aecca8b14b2dc687c381ca' + x
        sha = hashlib.sha1(x.encode('utf-8'))
        encrypts = sha.hexdigest()
        # sha1 x
        x = '20180111_android:' + encrypts
        ret = base64.b64encode(x.encode('utf-8'))
        ret = bytes.decode(ret)
        #print(ret, '111111111111')
        return ret



    def start_requests(self):
        set_len = self.url_db.scard('ke_citys:house_id_set')
        # url_db.sadd("ke_citys:house_id_set", json_data)
        #添加钉钉提示---2020-08-17
        start_ding_msg = '任务:租房带看{}---开始爬取{}---对列长度是{}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), 'ke_citys:house_id_set', set_len)
        self.dingding(start_ding_msg)
        while 1:
            house_infos = self.url_db.spop('ke_citys:house_id_set')
            if house_infos:
                if isinstance(house_infos, bytes):
                    house_infos = house_infos.decode()
                house_infos = json.loads(house_infos)
                house_info = house_infos.get('classid', '')

                bt_time = house_infos.get('bt_time', '')
                url = self.format_url.format(house_info, '0')
                jiami_url = url.split('seeRecordV2?')[-1]
                Authorization = self.auth(jiami_url)
                self.ori_headers['Authorization'] = Authorization
                self.logger.info('开始爬取的url是--{}'.format(url))

                yield scrapy.Request(url=url, headers=self.ori_headers, meta={'house_id': house_info, 'bt_time': bt_time}, callback=self.parse)
            else:
                #print('队列已消耗完毕，退出')
                self.logger.info('队列已消耗完毕，已退出！')
                end_ding_msg = '队列已消耗完毕,租房带看任务结束{}------成功对列长度是{}'.format(time.strftime('%Y-%m-%d %H:%M:%S'), self.url_db.scard('ke_citys:ershou_successful_set'))
                self.dingding(end_ding_msg)
                break
        # # ceshi
        # bt_time = '11111'
        # house_info = '107102785206'   #101106279522
        # url = 'https://app.api.ke.com/house/house/seeRecordV2?house_code={}&city_id=&limit_count=20&limit_offset=0'.format(house_info)
        # url = self.format_url.format(house_info, '0')
        # jiami_url = url.split('seeRecordV2?')[-1]
        # Authorization = self.auth(jiami_url)
        # self.ori_headers['Authorization'] = Authorization
        # yield scrapy.Request(url=url, headers=self.ori_headers, meta={'house_id': house_info,'bt_time': bt_time}, callback=self.parse)


    def parse(self, response):
        viewer_all_info = FangBeikeErShouViewerItem()
        room_id = response.meta.get('house_id', '')
        bt_time = response.meta.get('bt_time', '')
        now_page = response.meta.get('now_page', 0)
        json_data = json.loads(response.text)
        data_list = json_data.get('data', '').get('see_record_list', [])
        total_see_count = json_data.get('data', '').get('total_see_count', '')
        self.logger.info('----房间号是{},带看记录是{}次,现在爬取的是第{}页-------'.format(room_id, total_see_count, now_page))

        last_7day_see_count = json_data.get('data', '').get('last_7day_see_count', '')
        viewer_all_info['room_id'] = room_id
        viewer_all_info['total_see_count'] = total_see_count
        viewer_all_info['last_7day_see_count'] = last_7day_see_count
        for data_item in data_list:
            viewer_info = dict()
            agent_code = data_item.get('agent_code', '')
            agent_ucid = data_item.get('agent_ucid', '')
            online_status = data_item.get('online_status', '')
            agent_name = data_item.get('agent_name', '')
            good_rate = data_item.get('good_rate', '')
            shop_name = data_item.get('shop_name', '')
            agent_level = data_item.get('agent_level', '')
            see_time = data_item.get('see_time', '')
            viewer_info['agent_code'] = agent_code
            viewer_info['agent_ucid'] = agent_ucid
            viewer_info['online_status'] = online_status
            viewer_info['agent_name'] = agent_name
            viewer_info['good_rate'] = good_rate
            viewer_info['shop_name'] = shop_name
            viewer_info['agent_level'] = agent_level
            viewer_info['see_time'] = see_time
            viewer_info['batch_time'] = bt_time
            viewer_info['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 采集时间
            viewer_all_info.update(viewer_info)
            yield viewer_all_info

        if total_see_count >= 20:
            self.logger.info('----房间号是{}带看记录是{}次,需要进行翻页-------'.format(room_id, total_see_count))
            next_page_nums = int(total_see_count/20)
            for i in range(1, next_page_nums + 1):
                url = self.format_url.format(room_id, str(i*20))
                jiami_url = url.split('seeRecordV2?')[-1]
                Authorization = self.auth(jiami_url)
                self.ori_headers['Authorization'] = Authorization
                yield scrapy.Request(url=url, headers=self.ori_headers, meta={'house_id': room_id, 'bt_time': bt_time, 'now_page':i}, callback=self.parse)




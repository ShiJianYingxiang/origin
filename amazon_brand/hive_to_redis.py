# -*- coding: utf-8 -*-
# @Time    : 2020/8/25 17:01
# @Author  : swd
# @fun     :hive调度到redis中(每天一次)

import redis
import datetime
import json
import time
import requests
from pyhive import hive


try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None


class Check_mail_hive():
    def __init__(self):
        self.host = '172.20.207.6'
        self.port = 10000
        self.username = 'supdev'
        self.database = 'default'

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


    def connect_hive(self):
        conn = hive.Connection(host=self.host, port=self.port, username=self.username, database=self.database)
        cursor = conn.cursor()
        return cursor


    def hive_select(self, conn, select_id, brand_key):

        try:
            conn.execute(select_id)
            bt_time = time.strftime('%Y-%m-%d')
            for result in conn.fetchall():
                print(result[0], type(result[0]))
                # product_info = {}
                # product_info['pid'] = result[0]
                # product_info['bt_time'] = bt_time
                # product_info['search'] = 'key'
                # print(product_info, '---', brand_key)

                #多一个批次时间
                # if not url_db.sismember("amazon_brand:{}_product_set".format(brand_key), json.dumps(product_info)):
                #     url_db.sadd("amazon_brand:{}_product_set".format(brand_key), json.dumps(product_info))
                #     url_db.lpush("amazon_brand:{}_product_list".format(brand_key), json.dumps(product_info))

                #直接存放ID
                if not url_db.sismember("amazon_brand:{}_product_set".format(brand_key), result[0]):
                    url_db.sadd("amazon_brand:{}_product_set".format(brand_key), result[0])
                    url_db.lpush("amazon_brand:{}_product_list".format(brand_key), result[0])

        except Exception as e:
            print(e)
        finally:
            conn.close()


if __name__ == '__main__':
    check_mail = Check_mail_hive()
    conn = check_mail.connect_hive()
    queries0 = """select distinct pid as num 
  from ods.ods_amazon_wares_info where dt>='2020-01-01' and lower(brand_name) like '%anker%'"""
    check_mail.hive_select(conn, queries0, 'anker')

    # =========================================
    queries1 = """select distinct pid as num 
  from ods.ods_amazon_wares_info where dt>='2020-01-01' and lower(brand_name) like '%aukey%'"""
    check_mail.hive_select(conn, queries1, 'aukey')


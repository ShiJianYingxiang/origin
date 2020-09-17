import datetime
import time
import json
import requests
import redis
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

    def connect_hive(self):
        conn = hive.Connection(host=self.host, port=self.port, username=self.username, database=self.database)
        cursor = conn.cursor()
        return cursor


    def hive_select(self, conn, select_id):
        try:
            conn.execute(select_id)
            for result in conn.fetchall():
                # print(result)
                batch_time = time.strftime('%Y-%m-%d')
                item = {'pid': result[0], "batch_time":  batch_time}
                product_data = json.dumps(item)
                print(product_data, type(product_data))
                if not url_db.sismember('amazon_import:detail_set', product_data):
                    url_db.sadd('amazon_import:detail_set', product_data)
                    url_db.lpush('amazon_import:detail_list', product_data)

        except Exception as e:
            print(e)
        finally:
            conn.close()

if __name__ == '__main__':
    check_mail = Check_mail_hive()
    conn = check_mail.connect_hive()
    end_time = (datetime.datetime.now() - datetime.timedelta(days=5)).strftime('%Y-%m-%d')

    queries0 = """select distinct(productid) from ods.spider_invs_amazon_ware_list where productid_comments_nums is not null and productid_comments_nums >50 and productid_comments_content  is not null and batch='2020-09-04'"""
    check_mail.hive_select(conn, queries0)










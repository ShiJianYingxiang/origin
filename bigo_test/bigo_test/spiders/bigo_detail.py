import scrapy
import json
import requests
import time
from bigo_test.items import BigoTestItem
import redis

class BigoDetailSpider(scrapy.Spider):
    name = 'bigo_detail'
    # allowed_domains = ['bigotv.tv']
    # start_urls = ['http://bigotv.tv/']
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:79.0) Gecko/20100101 Firefox/79.0',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'referer': 'http://www.bigo.tv/',
    }
    headers1 = {
        'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.157 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest'
    }
    retry_count = 10
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'bigo_id_spider'
    today_time = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    bigo_id_item_set = '{}:{}_set'.format(base_key, today_time)    #去重是放在时间队列中去重
    bigo_id_item_list = '{}:item_list'.format(base_key)         #去重之后的都是放在一个整体的队列中
    no_liveing_key_set = '{}:nolive_set'.format(base_key)
    # ---------
    item = BigoTestItem()

    def start_requests(self):
        # str_len = self.url_db.llen(self.bigo_id_item_list)
        # if str_len > 0:
        #     for i in range(str_len):
        #         bigo_id_json = self.url_db.lpop(self.bigo_id_item_list)
        #         each = json.loads(bigo_id_json, encoding='utf-8')
        #
        #         # link = 'http://www.bigo.tv/' + str(each.get('extras', '').get('bigo_id', ''))
        #         # http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId=62802649&_=1599568527345
        #         link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(each.get('extras', '').get('bigo_id', '')))
        #         yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)
        # each = {"uid": "30258474", "online": "", "nickname": "Ara\uc544\ub77c\u0e53\u52a0\u6cb9\u0e53", "platform": "bigo", "fans": "", "batch": "2020-09-08 20:00:00", "extras": {"owner": 1523145101, "bigo_id": "30258474", "country": "Korea"}}
        # link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(each.get('extras', '').get('bigo_id', '')))
        # yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)
        while 1:
            bigo_id_json = self.url_db.lpop(self.bigo_id_item_list)
            if bigo_id_json:
                each = json.loads(bigo_id_json, encoding='utf-8')
                # link = 'http://www.bigo.tv/' + str(each.get('extras', '').get('bigo_id', ''))
                # http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId=62802649&_=1599568527345
                link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(each.get('extras', '').get('bigo_id', '')))
                yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)
            else:
                print('队列已消耗完毕，退出')
                break

        bigo_id_json = self.url_db.lpop(self.bigo_id_item_list)
        if bigo_id_json:
            each = json.loads(bigo_id_json, encoding='utf-8')
            # link = 'http://www.bigo.tv/' + str(each.get('extras', '').get('bigo_id', ''))
            # http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId=62802649&_=1599568527345
            link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(
                str(each.get('extras', '').get('bigo_id', '')))
            yield scrapy.Request(url=link, meta={'datas': each}, headers=self.headers, callback=self.parse)




    def parse(self, response):
        print(response.text)
        data_json = response.meta.get('datas', '')
        retry_count = response.meta.get('retry_count', 0)  #
        # contribution_value = response.xpath('//i[@class="beans"]/text()').get()
        # contry_area = response.xpath('//i[@class="country"]/text()').get()
        error_occurred = False

        data = json.loads(response.text)
        try:
            assert data
            data = json.loads(response.text)
            assert data['code'] == 0 and data['msg'] == 'success', '状态码错误'
        except Exception as e:
            self.logger.info('礼物详情信息失败,错误信息:{}, 原始返回内容:{}'.format(e, data))
            error_occurred = True
            # return None
        if error_occurred and retry_count < self.retry_count:
            link = 'http://www.bigo.tv/OUserCenter/getUserInfoStudio?bigoId={}'.format(str(data_json.get('extras', '').get('bigo_id', '')))
            yield scrapy.Request(url=link, meta={'datas': data_json}, headers=self.headers, callback=self.parse)

        contribution_value = data.get('data', '').get('bean', '')

        data_json['contribution'] = contribution_value   #贡献值
        data_json['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))   #抓取时间
        self.item['cat1'] = '秀场'
        self.item['cat2'] = ''
        self.item.update(data_json)
        print(self.item)
        # yield self.item


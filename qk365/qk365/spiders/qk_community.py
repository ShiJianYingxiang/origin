# -*- coding: utf-8 -*-
'''
详情页是抓取小程序获取的接口信息
房管员和小区信息是通过抓取到的房间id拼接pc端的链接进行获取
'''
import scrapy
import re
import math
import json
import time
from qk365.items import Qk365Item
from qk365.items import Qk365DealerItem
from qk365.items import Qk365CommunityItem
# from qk365.items import Qk365NextItem

class QkHotelSpider(scrapy.Spider):
    name = 'qk_community'
    # allowed_domains = ['qk365.com']
    start_urls = ['https://www.qk365.com/']
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
    }
    item = Qk365Item()
    dealeritem = Qk365DealerItem()
    communityitem = Qk365CommunityItem()
    # parsenextitem = Qk365NextItem()
    room_url = "https://mp.qk365.com/room/queryRoomDetail"

    def parse(self, response):
        # 拼接所有城市小区链接
        city_urls = response.xpath('''//div[@class="popupHide"]//a//@href''').getall()
        for city_url in city_urls:
            city_url = city_url + '/xiaoqu'
            yield scrapy.Request(url=city_url, headers=self.headers, callback=self.hotel_num_page)
        # city_url = 'https://www.qk365.com/list'
        # yield scrapy.Request(url=city_url, headers=self.headers, callback=self.hotel_num_page)


    def hotel_num_page(self,response):
        #解析每个城市下的小区总数目并计算出翻页数目
        nums_content = response.xpath('''//div[@class="SortSel fR"]/em''').get()

        community_nums = re.search('(\d+)', nums_content).group()   #获取总的小区数目
        community_page_nums = math.ceil(int(community_nums)/21)    # 获取翻页数
        if community_page_nums > 0:
            for page_temp in range(1, community_page_nums+1):
                community_page_url = response.url + '/p' + str(page_temp)
                # 发送翻页请求
                yield scrapy.Request(url=community_page_url, headers=self.headers, callback=self.total_community_url)
        # city_page_url = 'https://www.qk365.com/list/p1'  |https://bj.qk365.com/xiaoqu/p2
        # yield scrapy.Request(url=city_page_url, headers=self.headers, callback=self.total_room_id_detail)

    def total_community_url(self, response):
        # 获取到小区链接  https://bj.qk365.com/xiaoqu/v24613
        community_url_list = response.xpath('''//div[contains(@class,"village-list")]//ul[@class="village-list"]//li/a/@href''').getall()
        for community_url in community_url_list:
            if community_url:
                yield scrapy.Request(url=community_url, headers=self.headers, callback=self.total_community_page)

    def total_community_page(self, response):
        # 获取小区下的房源数目---确定翻页数
        # https://www.qk365.com/xiaoqu/v24600-p1
        community_room_total_nums = response.xpath('''//div[@class="area fL"]//p/em/text()''').get()

        page_total_nums = math.ceil(int(community_room_total_nums)/9)    # 获取翻页数
        if page_total_nums > 0:
            for page_temp in range(1, page_total_nums+1):

                community_url_page = response.url + '-p' + str(page_temp)
                # 提交请求，获取所有的房间id
                yield scrapy.Request(url=community_url_page, headers=self.headers, callback=self.get_more_roomid)


    def get_more_roomid(self, response):
        '''获取小区下的所有房屋id'''
        all_hotel_id = response.xpath('''//div[contains(@class,"related-box")]//div[contains(@class,"House_List_Box")]//h3/a/@href''').getall()
        headers1 = {
            "Host": "mp.qk365.com",
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; KIW-AL10 Build/HONORKIW-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm64',
            'content-type': 'application/json',
        }
        for hotel_id in all_hotel_id:
            room_id = re.search('room/(\d+)', hotel_id).group(1)
            if room_id:
                data = {'roomId': room_id}   #小程序入口比APP多一些字段，发送所有房屋的详情请求
                yield scrapy.Request(url=self.room_url, headers=headers1, body=json.dumps(data), meta={"room_id": room_id}, method='post', callback=self.parse_next_room_detail_info)

                room_url = 'https://www.qk365.com/room/%s' % str(room_id)  #获取小区信息和房管员信息
                yield scrapy.Request(url=room_url, headers=self.headers, meta={'roomId': room_id}, callback=self.pc_room_detail)
        # print('=============----------------------------------==========')

    def parse_next_room_detail_info(self, response):
        data = json.loads(response.text).get('data', '')
        page_roomid = response.meta.get('room_id', '')
        roomid = data.get('roomId', '')
        if not roomid:
            self.logger.error(page_roomid)
        else:
            self.item['crawl_source'] = 'community'  #判断抓取来源---(小区、经纪人、正常城市扫描)
            for temp_key, temp_value in data.items():
                self.item['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
                self.item[temp_key] = temp_value
                if temp_key == 'ceaId':
                    self.item['ceaId'] = 'k' + str(data.get('ceaId', ''))
                if temp_key == 'prcId':
                    self.item['prcId'] = 'a' + str(data.get('prcId', ''))
                if temp_key == 'villageId':
                    self.item['villageId'] = 'v' + str(data.get('villageId', ''))
                if temp_key == 'rentDateName':
                    rent_status = data.get('rentDateName', '')
                    #print(rent_status, '--------', type(rent_status))
                    if rent_status:
                        if '立即' in rent_status:
                            self.item['rent_status'] = '待租'
                        else:
                            self.item['rent_status'] = '已租'
            yield self.item

    def pc_room_detail(self, response):
        '''============公有的====================='''
        roomid = response.meta.get('roomid', '')
        region = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/text()''').get()  #房山区

        region_id_content = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/@href''').get()  # 需要正则

        if region_id_content:
            region_id = re.search('list/(\w+\d+)', region_id_content).group(1)
        else:
            return
        district = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[2]/text()''').get()  #地区
        district_id_content = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[2]/@href''').get()  # 需要正则
        if district_id_content:
            district_id = re.search('-(\w+\d+)', district_id_content).group(1)
        else:
            district_id = ''


        detail_url = response.xpath('''//p[@class="stewPhotName"]//a/@href''').get()  #房管员url---id
        dealer_code = response.xpath('''//input[@id="romAdminId"]/@value''').get()  #房管员id
        dealer_name = response.xpath('''//p[@class="stewPhotName"]//a/text()''').get()   #房管员名称---房管员：刘英迪1
        dealer_name = str(dealer_name).replace('房管员：', '').strip()
        rent_turnover_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[last()]/text()''').get()  #8间
        rent_house_count_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[1]/text()''').get()  #127间
        service_people_count_content = response.xpath('''(//p[@class="stewPhotinfo"]//em)[2]/text()''').get()  #36人
        try:
            rent_turnover = re.search('\d+', rent_turnover_content).group() if rent_turnover_content else 0
        except:
            rent_turnover = 0
        try:
            rent_house_count = re.search('\d+', rent_house_count_content).group() if rent_house_count_content else 0
        except:
            rent_house_count = 0
        try:
            service_people_count = re.search('\d+', service_people_count_content).group() if service_people_count_content else 0
        except:
            service_people_count = 0
        self.dealeritem['roomId'] = roomid
        self.dealeritem['region'] = region
        self.dealeritem['region_id'] = region_id
        self.dealeritem['district'] = district
        self.dealeritem['district_id'] = district_id
        self.dealeritem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.dealeritem['detail_url'] = detail_url
        self.dealeritem['dealer_code'] = dealer_code
        self.dealeritem['dealer_name'] = dealer_name
        self.dealeritem['rent_turnover'] = rent_turnover
        self.dealeritem['rent_house_count'] = rent_house_count
        self.dealeritem['service_people_count'] = service_people_count
        yield self.dealeritem
        # ###############################
        community_code_content = response.xpath('''//div[@class="survey-left fL"]//dd/a/@href''').get()  #
        if community_code_content:
            community_code = re.search('xiaoqu/(\w+\d+)', community_code_content).group(1)    #小区id
        else:
            community_code = ''
        community_name = response.xpath('''//div[@class="survey-left fL"]//dd/a/text()''').get()  # 小区名称
        longitude = response.xpath('''//input[@id="cucLongitude"]/@value''').get()  # 经度
        latitude = response.xpath('''//input[@id="cucLatitude"]/@value''').get()  # 纬度
        self.communityitem['roomId'] = roomid
        self.communityitem['region'] = region
        self.communityitem['region_id'] = region_id
        self.communityitem['district'] = district
        self.communityitem['district_id'] = district_id
        self.communityitem['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S')
        self.communityitem['community_code'] = community_code
        self.communityitem['community_name'] = community_name
        self.communityitem['longitude'] = longitude
        self.communityitem['latitude'] = latitude
        yield self.communityitem


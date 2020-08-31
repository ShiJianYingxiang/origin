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
    name = 'qk_hotel'
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
        # 获取所有城市属地链接
        city_urls = response.xpath('''//div[@class="popupHide"]//a//@href''').getall()
        for city_url in city_urls:
            city_url = city_url + '/list'
            yield scrapy.Request(url=city_url, headers=self.headers, callback=self.hotel_num_page)



    def hotel_num_page(self,response):
        #解析每个城市下的房间数目并计算出翻页数目
        nums_content = response.xpath('''//div[@class="SortSel fR"]/em''').get()  #获取总的房间数目
        hotel_nums = re.search('(\d+)', nums_content).group()   #获取房间数
        hotel_page_nums = math.ceil(int(hotel_nums)/21)    # 获取翻页数
        if hotel_page_nums > 0:
            for page_temp in range(1, hotel_page_nums+1):
                city_page_url = response.url + '/p' + str(page_temp)
                # 发送翻页请求
                yield scrapy.Request(url=city_page_url, headers=self.headers, callback=self.total_room_id_detail)


    def total_room_id_detail(self, response):
        # print(response.url, '==========city_page_url==========')
        room_id_list = response.xpath('''//div[contains(@class,"w1170")]//ul[@class="easyList"]//li/a/@href''').getall()
        for room_id_temp in room_id_list:
            room_id = re.search('room/(\d+)', room_id_temp).group(1)
            if room_id:
                room_url = response.urljoin(room_id).replace('list', 'room')

            # if room_id:
            #     room_url = 'https://www.qk365.com/room/%s'%str(room_id)   #获取到房屋id（列表中推荐的|处于待租状态的）直接进pc端的详情页，获取更多的房屋信息
                # print(room_url,'--------page_all_detail_room_url----------------------')
                yield scrapy.Request(url=room_url, headers=self.headers, meta={'room_id': room_id}, callback=self.get_more_roomid)
    #

    def get_more_roomid(self, response):
        '''获取所有房屋id(包括已出租的|待出租的)'''

        host_room_id = response.meta.get('room_id', '')

        all_hotel_id = response.xpath('''/html/body/div[12]/div/div[1]/div/div[1]/div[1]/div/table/tbody//tr/td[1]/a/@href|//tr//td[@class="houLetter houLine"]/a/@href|//div[@class="houmTab"]//tr//td[@class="houLetter houLine"]/a/@href''').getall()

        headers1 = {
            "Host": "mp.qk365.com",
            'User-Agent': 'Mozilla/5.0 (Linux; Android 5.1.1; KIW-AL10 Build/HONORKIW-AL10; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.99 Mobile Safari/537.36 MicroMessenger/7.0.12.1620(0x27000C50) Process/appbrand0 NetType/WIFI Language/zh_CN ABI/arm64',
            'content-type': 'application/json',
        }
        if len(all_hotel_id) == 0:

            yield scrapy.Request(url=response.url, headers=self.headers, meta={'roomid': host_room_id},
                                 callback=self.pc_room_detail)
        else:
            for hotel_id in all_hotel_id:
                room_id = re.search('room/(\d+)', hotel_id).group(1)
                if room_id:
                    data = {'roomId': room_id}   #小程序入口比APP多一些字段，发送所有房屋的详情请求
                    yield scrapy.Request(url=self.room_url, headers=headers1, body=json.dumps(data), meta={"room_id": room_id}, method='post', callback=self.parse_next_room_detail_info)  #post请求获取详细信息

                    room_url = response.urljoin(room_id).replace('list', 'room')
                    yield scrapy.Request(url=room_url, headers=self.headers, meta={'roomid': room_id}, callback=self.pc_room_detail)


    def parse_next_room_detail_info(self, response):
        page_roomid = response.meta.get('room_id','')
        data = json.loads(response.text).get('data', '')
        roomid = data.get('roomId', '')
        if not roomid:
            self.logger.error(page_roomid)
        else:
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
    #
    def pc_room_detail(self, response):
        '''============公有的====================='''
        # print(response.url, '------------last_room_url---------------------')
        roomid = response.meta.get('roomid', '')

        region = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/text()''').get()  #房山区

        region_id_content = response.xpath('''((//div[@class="survey-right fR"]//dd)[last()]/a)[1]/@href''').get()  # 需要正则

        if region_id_content:
            region_id = re.search('list/(\w+\d+)', region_id_content).group(1)
        else:
            region_id = ''
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
        # print(dealer_name)
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


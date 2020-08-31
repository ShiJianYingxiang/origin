# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
import redis
from fang_beike.items import FangBeikeItem



class GetCitiesRankSpider(scrapy.Spider):
    name = 'get_cities_rank'
    custom_settings = {
        # 设置log日志
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': './././Log/scrapy_{}_{}.log'.format('rank', time.strftime('%Y-%m-%d'))
    }
    headers = {
        'Host': 'm.ke.com',
        'Accept': 'application/json, text/plain, */*',
        'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; MI 5 Build/MXB48T; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/51.0.2704.81 Mobile Safari/537.36 lianjiabeike/2.39.0',
        # 'Referer': 'https://m.ke.com/sh/fang/tool/rankingList?city_id=310000&type=renqi&district_id=310116',
        'Accept-Language': 'zh-CN,en-US;q=0.8',
        'Cookie': 'lianjia_ssid=567844a9-c641-4cb9-9797-eaf0de071bc7; lianjia_token=; lianjia_udid=861322030797829; lianjia_uuid=345eab00-91c3-4de7-8317-3b1aeb972fb8; select_city=150100; staticData=%7B%22appName%22%3A%22%E8%B4%9D%E5%A3%B3%E6%89%BE%E6%88%BF%22%2C%22appVersion%22%3A%222.39.0%22%2C%22deviceId%22%3A%22861322030797829%22%2C%22deviceInfo%22%3A%7B%22duid%22%3A%22DuGmaBC3rNBWAoWOPjZrbXZapgmiL9opFFTNqU%2BnuEegz7Yb6i2cOkI1aGTOlHuqe%2FfOQXdmm0y%2Bqrfe0LcRmDAA%22%2C%22ssid%22%3A%22567844a9-c641-4cb9-9797-eaf0de071bc7%22%2C%22udid%22%3A%22861322030797829%22%2C%22uuid%22%3A%22345eab00-91c3-4de7-8317-3b1aeb972fb8%22%7D%2C%22extraData%22%3A%7B%22cityId%22%3A%22150100%22%2C%22cityName%22%3A%22%E5%91%BC%E5%92%8C%E6%B5%A9%E7%89%B9%22%2C%22latitude%22%3A%2240.016667%22%2C%22locationCityId%22%3A%22110000%22%2C%22locationCityName%22%3A%22%E5%8C%97%E4%BA%AC%22%2C%22longitude%22%3A%22116.476506%22%2C%22wifiName%22%3A%22DATABURNING%22%7D%2C%22network%22%3A%22WIFI%22%2C%22scheme%22%3A%22lianjiabeike%22%2C%22sysModel%22%3A%22android%22%2C%22sysVersion%22%3A%22Android+6.0.1%22%2C%22userInfo%22%3A%7B%7D%7D; lianjia_token=; lianjia_uuid=345eab00-91c3-4de7-8317-3b1aeb972fb8; lianjia_udid=861322030797829; csrfToken=FHkjYYXZQpe5jfR69p10carp; digv_extends={"utmTrackId":null}; select_city=110000; rank_city_id=110000; srcid=eyJ0IjoiXCJ7XFxcImRhdGFcXFwiOlxcXCJmNDFhZTFhM2ZlYjZiMWI3OTM3ZjI0N2IxNDFjMDg4ZDA5N2VhMmM2YTZiYmQxMjJiY2M2ZGE5ZjkxM2ViNjZlYzUwNmU3OWQ3MGE0YzY4NWRiYzdhZTExNDg1YTk3ODkwZjYyODc1ZjY4NGMxYWJmMDZjN2MyNWQ2OTc2MDkzM2Y0OTdlNzI4ZWY0ZGE3MmRhZWIyNTVhY2I2OThmN2IwYTZhZjNiMjUyOWVlYTFmZjM4YTQxYjA0NmIyNDA4N2JjZTk5MTY3MDA3YWZhYWZlODE1NGQ1NjdlMjVkMmQ3YTBhNjUyMDc3ODc2NjdmYzY5NjA3Y2M1ZDYzMTE0NWFjMDFjYWYxMWEzMmU0MzRjOWNiZmI1MDY0OTBmZWFjMTIxY2Q1ZTEzZGZiMDZlMGQ0NWQ2NDQ0OWZlMjQzYTA1OGE0N2U2OGFkNjU1OGRkZGQ1NmI5OWQ0NTZkMmRhZTcwXFxcIixcXFwia2V5X2lkXFxcIjpcXFwiMVxcXCIsXFxcInNpZ25cXFwiOlxcXCJkNDdmMWIwZlxcXCJ9XCIiLCJyIjoiaHR0cHM6Ly9tLmtlLmNvbS9zaC9mYW5nL3Rvb2wvcmFua2luZ0xpc3Q/Y2l0eV9pZD0zMTAwMDAmdHlwZT1yZW5xaSZkaXN0cmljdF9pZD0zMTAxMTYiLCJvcyI6IndlYiIsInYiOiIwLjEifQ==; lianjia_ssid=567844a9-c641-4cb9-9797-eaf0de071bc7',
        'X-Requested-With': 'com.lianjia.beike',
    }
    try:
        # url_db = redis.StrictRedis(host='112.126.102.89', port=6379, db=7, password='dalian')
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None



    def start_requests(self):
        self.logger.info('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
        citys_area_info_list = self.url_db.lrange('ke_citys:citys_area_list_0', 0, -1)
        for citys_area_info in citys_area_info_list:
            if citys_area_info:
                if isinstance(citys_area_info, bytes):
                    citys_area_info = citys_area_info.decode()
                    citys_area_info = json.loads(citys_area_info)
                rank_url = 'https://m.ke.com/{0}/fang/tool/api/rank/list?city_id={1}&district_id={2}&type=chengjiao'.format(citys_area_info.get('abbr', ''), citys_area_info.get('id', ''), citys_area_info.get('area_id', ''))
                yield scrapy.Request(url=rank_url, headers=self.headers, meta={'area_info': citys_area_info}, callback=self.parse)
        # rank_url = 'https://m.ke.com/bj/fang/tool/api/rank/list?city_id=110000&district_id=0&type=chengjiao'
        # yield scrapy.Request(url=rank_url, headers=self.headers, callback=self.parse)



    def parse(self, response):
        area_info = response.meta.get('area_info', '')
        json_data = json.loads(response.text)
        data_list = json_data.get('data', '').get('list', [])
        self.logger.info('抓取的区域信息是{}，获取榜单的个数是{},对应的url是：{}'.format(area_info, len(data_list), response.url))
        for data_item in data_list:
            room_info = FangBeikeItem()
            pid = data_item.get('pid', '')  #
            id = data_item.get('id', '')  #
            city_id = data_item.get('city_id', '')  # 城市ID
            city_name = data_item.get('city_name', '')  # 城市名称
            min_frame_area = data_item.get('min_frame_area', '')  # 最小建筑面积
            max_frame_area = data_item.get('max_frame_area', '')  # 最大建筑面积
            district_name = data_item.get('district_name', '')  # 区域名称
            district = data_item.get('district', '')  # 区域名称
            district_id = data_item.get('district_id', '')  # 区域ID
            bizcircle_id = data_item.get('bizcircle_id', '')  # ??
            bizcircle_name = data_item.get('bizcircle_name', '')  # 通州其它
            build_id = data_item.get('build_id', '')  # ??
            process_status = data_item.get('process_status', '')
            resblock_frame_area = data_item.get('resblock_frame_area', '')
            resblock_frame_area_range = data_item.get('resblock_frame_area_range', '')
            decoration = data_item.get('decoration', '')  # 精装修
            longitude = data_item.get('longitude', '')  # 经纬度
            latitude = data_item.get('latitude', '')  # 经纬度
            frame_rooms_desc = data_item.get('frame_rooms_desc', '')  # 户型
            title = data_item.get('title', '')  # 招商·臻珑府
            address = data_item.get('address', '')  # 地址
            store_addr = data_item.get('store_addr', '')  # 售楼店铺地址
            average_price = data_item.get('average_price', '')  # 均价
            house_type = data_item.get('house_type', '')  # 房屋用途---住宅
            sale_status = data_item.get('sale_status', '')  # 是否在售
            open_date = data_item.get('open_date', '')  # 开盘日期
            lowest_total_price = data_item.get('lowest_total_price', '')  # 总价
            show_price = data_item.get('show_price', '')  # 47000
            show_price_unit = data_item.get('show_price_unit', '')  # 元/平
            show_price_desc = data_item.get('show_price_desc', '')  # 均价
            show_price_info = data_item.get('show_price_info', '')  # 均价47000元/平
            developer_company = data_item.get('developer_company', '')  # 开发商--['北京经开亦盛房地产开发有限公司']
            project_desc = data_item.get('project_desc', '')  #
            rank = data_item.get('rank', '')  # 排名
            rank_reason = data_item.get('rank_reason', '')  # 排名原因
            room_info['pid'] = pid
            room_info['id'] = id
            room_info['city_id'] =city_id
            room_info['city_name'] = city_name
            room_info['min_frame_area'] = min_frame_area
            room_info['max_frame_area'] = max_frame_area
            room_info['district_name'] = district_name
            room_info['district'] = district
            room_info['district_id'] = district_id
            room_info['bizcircle_id'] = bizcircle_id
            room_info['bizcircle_name'] = bizcircle_name
            room_info['build_id'] = build_id
            room_info['process_status'] = process_status
            room_info['resblock_frame_area'] = resblock_frame_area
            room_info['resblock_frame_area_range'] = resblock_frame_area_range
            room_info['decoration'] = decoration
            room_info['longitude'] = longitude
            room_info['latitude'] = latitude
            room_info['frame_rooms_desc'] = frame_rooms_desc
            room_info['title'] = title
            room_info['address'] = address
            room_info['store_addr'] = store_addr
            room_info['average_price'] = average_price
            room_info['house_type'] = house_type
            room_info['sale_status'] = sale_status
            room_info['open_date'] = open_date
            room_info['lowest_total_price'] = lowest_total_price
            room_info['show_price'] = show_price
            room_info['show_price_unit'] = show_price_unit
            room_info['show_price_desc'] = show_price_desc
            room_info['show_price_info'] = show_price_info
            room_info['developer_company'] = developer_company
            room_info['project_desc'] = project_desc
            room_info['rn'] = rank
            room_info['rank_reason'] = rank_reason
            room_info['batch_time'] = time.strftime('%Y-%m-%d %H') + ':00:00'
            room_info['crawl_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 采集时间
            yield room_info
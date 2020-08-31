# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FangBeikeItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pid = scrapy.Field()              #
    id = scrapy.Field()               #
    city_id = scrapy.Field()          #城市ID
    city_name = scrapy.Field()        #城市名称
    min_frame_area = scrapy.Field()   #最小建筑面积
    max_frame_area = scrapy.Field()   #最大建筑面积
    district_name = scrapy.Field()   #区域名称
    district = scrapy.Field()       #区域名称
    district_id = scrapy.Field()    #区域ID
    bizcircle_id = scrapy.Field()   #??
    bizcircle_name = scrapy.Field()  #通州其它
    build_id = scrapy.Field()       #??
    process_status = scrapy.Field()
    resblock_frame_area = scrapy.Field()
    resblock_frame_area_range = scrapy.Field()
    decoration = scrapy.Field()    #精装修
    longitude = scrapy.Field()     #经纬度
    latitude = scrapy.Field()      #经纬度
    frame_rooms_desc = scrapy.Field() #户型
    title = scrapy.Field()         #招商·臻珑府
    address = scrapy.Field()       #地址
    store_addr = scrapy.Field()    #售楼店铺地址
    average_price = scrapy.Field()  #均价
    house_type = scrapy.Field()  #房屋用途---住宅
    sale_status = scrapy.Field()  #是否在售
    open_date = scrapy.Field()  #开盘日期
    lowest_total_price = scrapy.Field()  #总价
    show_price = scrapy.Field()  #47000
    show_price_unit = scrapy.Field()  #元/平
    show_price_desc = scrapy.Field()  #均价
    show_price_info = scrapy.Field()  #均价47000元/平
    developer_company = scrapy.Field()  #开发商--['北京经开亦盛房地产开发有限公司']
    project_desc = scrapy.Field()  #
    rn = scrapy.Field()  #排名
    rank_reason = scrapy.Field()  # 排名原因
    batch_time = scrapy.Field()  #批次时间
    crawl_time = scrapy.Field()  #抓取时间

# 二手房带看记录
class FangBeikeErShouViewerItem(scrapy.Item):
    room_id = scrapy.Field()  # 房子ID
    total_see_count = scrapy.Field()  #累计带看次数
    last_7day_see_count = scrapy.Field()  #近7日带看次数
    agent_code = scrapy.Field()  #带看人编号
    agent_ucid = scrapy.Field()  #带看人
    online_status = scrapy.Field()  #带看人在职状态
    agent_name = scrapy.Field()  #带看人姓名
    good_rate = scrapy.Field()  #带看人好评率
    shop_name = scrapy.Field()  #带看人所属店铺
    agent_level = scrapy.Field()  #带看人等级
    see_time = scrapy.Field()  #带看时间
    batch_time = scrapy.Field()  #批次时间
    crawl_time = scrapy.Field()  #抓取时间
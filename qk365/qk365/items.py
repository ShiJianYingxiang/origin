# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class Qk365Item(scrapy.Item):
    # define the fields for your item here like:
    crawl_time = scrapy.Field()
    roomId = scrapy.Field()
    roomCode = scrapy.Field()
    roomTitle = scrapy.Field()
    roomLock = scrapy.Field()
    roomPrestate = scrapy.Field()
    roomCancel = scrapy.Field()
    metroId = scrapy.Field()
    metroName = scrapy.Field()
    metroStationId = scrapy.Field()
    metroStationName = scrapy.Field()
    metroDistance = scrapy.Field()
    metroInfoList = scrapy.Field()
    busId = scrapy.Field()
    busName = scrapy.Field()
    busStationId = scrapy.Field()
    busStationName = scrapy.Field()
    busDistance = scrapy.Field()
    busInfoList = scrapy.Field()
    roomLevel = scrapy.Field()
    roomLevelStr = scrapy.Field()
    roomRent = scrapy.Field()
    roomSellingPrice = scrapy.Field()
    roomVipSellingPrice = scrapy.Field()
    roomSpecialOffer = scrapy.Field()
    cucId = scrapy.Field()
    cucFloor = scrapy.Field()
    cucTotalFloor = scrapy.Field()
    prcId = scrapy.Field()
    prcName = scrapy.Field()
    ceaId = scrapy.Field()
    ceaName = scrapy.Field()
    villageId = scrapy.Field()
    villageName = scrapy.Field()
    villageAddress = scrapy.Field()
    roomCoverPhotoSmall = scrapy.Field()
    roomCoverPhotoMid = scrapy.Field()
    roomCoverPhotoBig = scrapy.Field()
    roomVideoUrl = scrapy.Field()
    room360VideoUrl = scrapy.Field()
    roomState = scrapy.Field()
    roomDiscountMinprice = scrapy.Field()
    roomDiscountMaxprice = scrapy.Field()
    roomVacantDate = scrapy.Field()
    villageLongitude = scrapy.Field()
    villageLatitude = scrapy.Field()
    roomAdminId = scrapy.Field()
    roomAdminName = scrapy.Field()
    roomAdminMobile = scrapy.Field()
    cityName = scrapy.Field()
    roomRecommType = scrapy.Field()
    cityId = scrapy.Field()
    roomView = scrapy.Field()
    showPrice = scrapy.Field()
    roomTypeId = scrapy.Field()
    activityName = scrapy.Field()
    roomAddress = scrapy.Field()
    imageList = scrapy.Field()
    orientation = scrapy.Field()
    roomType = scrapy.Field()
    rentDateName = scrapy.Field()
    facility = scrapy.Field()
    roomFacility = scrapy.Field()
    oneWordRecommendations = scrapy.Field()
    roomLabels = scrapy.Field()
    activityId = scrapy.Field()
    activityLabelName = scrapy.Field()
    activityLabelPosition = scrapy.Field()
    activityLabelDescription = scrapy.Field()
    activityUrl = scrapy.Field()
    activityLabelStyle = scrapy.Field()
    simpleMetroName = scrapy.Field()
    formatRoomRent = scrapy.Field()
    formatShowPrice = scrapy.Field()
    randomRoomCoverPhoto = scrapy.Field()
    rent_status = scrapy.Field()
    crawl_source = scrapy.Field()

class Qk365DealerItem(scrapy.Item):
    crawl_time = scrapy.Field()
    dealer_code = scrapy.Field()      #售房人id
    dealer_name = scrapy.Field()      #售房人名称
    rent_turnover = scrapy.Field()     #近30天出房数量
    rent_house_count = scrapy.Field()  #房源数量
    service_people_count = scrapy.Field()  #服务人数
    region = scrapy.Field()           #区域
    region_id = scrapy.Field()        #区域id
    district = scrapy.Field()         #地区
    district_id = scrapy.Field()      #地区id
    detail_url = scrapy.Field()       #房管员url
    roomId = scrapy.Field()


class Qk365CommunityItem(scrapy.Item):
    community_code = scrapy.Field()   #小区id
    community_name = scrapy.Field()   #小区名称
    longitude = scrapy.Field()        #经度
    latitude = scrapy.Field()         #纬度
    region = scrapy.Field()           #区域
    region_id = scrapy.Field()        #区域id
    district = scrapy.Field()         #地区
    district_id = scrapy.Field()      #地区id
    crawl_time = scrapy.Field()
    roomId = scrapy.Field()



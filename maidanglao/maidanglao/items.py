# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class MaidanglaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    _id = scrapy.Field()
    _location = scrapy.Field()
    _name = scrapy.Field()
    _address = scrapy.Field()
    StoreName_EN = scrapy.Field()
    HasMobileOffers = scrapy.Field()
    StoreName_CN = scrapy.Field()
    IsDriveThrough = scrapy.Field()
    ZipCode = scrapy.Field()
    HasMobileOrdering = scrapy.Field()
    HasMDS = scrapy.Field()
    HasWifi = scrapy.Field()
    StoreCode = scrapy.Field()
    Is24 = scrapy.Field()
    CityName_CN = scrapy.Field()
    LocationY = scrapy.Field()
    CityName_EN = scrapy.Field()
    LocationX = scrapy.Field()
    PhoneNumber = scrapy.Field()
    id = scrapy.Field()
    HasMcCafe = scrapy.Field()
    StoreAddress_EN = scrapy.Field()
    HasPlayland = scrapy.Field()
    HasKIOSK = scrapy.Field()
    StoreAddress_CN = scrapy.Field()
    IsOpen = scrapy.Field()
    _createtime = scrapy.Field()
    _updatetime = scrapy.Field()
    _province = scrapy.Field()
    _city = scrapy.Field()
    _district = scrapy.Field()
    _image = scrapy.Field()

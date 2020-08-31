# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BigoTestItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    cat1 = scrapy.Field()
    cat2 = scrapy.Field()
    uid = scrapy.Field()
    online = scrapy.Field()     #在线
    nickname = scrapy.Field()   #昵称
    platform = scrapy.Field()   #平台
    fans = scrapy.Field()   #粉丝数
    contribution = scrapy.Field()  #贡献
    crawl_time = scrapy.Field()  #抓取时间
    batch = scrapy.Field()   #时间
    extras = scrapy.Field()   #大的字典

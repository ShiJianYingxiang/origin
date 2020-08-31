# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class YoudaoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    tag_id = scrapy.Field()
    crawl_time = scrapy.Field()
    class_content = scrapy.Field()  #一个大的串
    categoryName = scrapy.Field()
    courseOriginalPrice = scrapy.Field()
    courseSaleNum = scrapy.Field()
    courseSalePrice = scrapy.Field()
    courseSaleTime = scrapy.Field()
    courseStartTime = scrapy.Field()
    courseTime = scrapy.Field()
    courseTitle = scrapy.Field()
    expireDate = scrapy.Field()
    hideNum = scrapy.Field()
    id = scrapy.Field()
    iosSalePrice = scrapy.Field()
    itemType = scrapy.Field()
    lessonNum = scrapy.Field()
    limitNum = scrapy.Field()
    liveStatus = scrapy.Field()
    needAddress = scrapy.Field()
    promotionId = scrapy.Field()
    promotionType = scrapy.Field()
    purchased = scrapy.Field()
    rank = scrapy.Field()
    registrationDeadline = scrapy.Field()
    saleStartTime = scrapy.Field()
    status = scrapy.Field()
    subCategories = scrapy.Field()
    teacherList = scrapy.Field()
    lessonTime = scrapy.Field()
    renew = scrapy.Field()
    saleEndTime = scrapy.Field()
    # ------详细的课程信息-------------
    isDemo = scrapy.Field()
    title = scrapy.Field()
    type = scrapy.Field()
    subTitle = scrapy.Field()
    liveTime = scrapy.Field()
    startTime = scrapy.Field()
    level = scrapy.Field()
    oldLessonId = scrapy.Field()
    validTime = scrapy.Field()
    endTime = scrapy.Field()
    status = scrapy.Field()
    product_id = scrapy.Field()
    planNum = scrapy.Field()
    list = scrapy.Field()
    video = scrapy.Field()
    assistantEndTime = scrapy.Field()
    assistantStartTime = scrapy.Field()
    videoDuration = scrapy.Field()
    liveId = scrapy.Field()
    entityUrl = scrapy.Field()
    expireTime = scrapy.Field()
    quizList = scrapy.Field()
    articleId = scrapy.Field()
    courseTvImage = scrapy.Field()
    # ------------老师的信息-------------
class Youdaoteacher_Item(scrapy.Item):
    crawl_time = scrapy.Field()
    product_id = scrapy.Field()
    id = scrapy.Field()
    name = scrapy.Field()
    imgUrl = scrapy.Field()
    tag_id = scrapy.Field()

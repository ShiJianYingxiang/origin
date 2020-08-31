# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class LebokeItem(scrapy.Item):
    # define the fields for your item here like:
    year = scrapy.Field()
    classCode = scrapy.Field()
    className = scrapy.Field()
    subjectCode = scrapy.Field()
    subjectName = scrapy.Field()
    mode = scrapy.Field()
    beginTime = scrapy.Field()
    endTime = scrapy.Field()
    printTime = scrapy.Field()
    teacherCode = scrapy.Field()
    teacherName = scrapy.Field()
    teacherPortrait = scrapy.Field()
    sex = scrapy.Field()
    lessonCount = scrapy.Field()
    lessonTimes = scrapy.Field()
    timeNum = scrapy.Field()
    applyTime = scrapy.Field()
    currentTime = scrapy.Field()
    classStatus = scrapy.Field()
    classType = scrapy.Field()
    beginLessonNo = scrapy.Field()
    price = scrapy.Field()
    originalPrice = scrapy.Field()
    count = scrapy.Field()
    buyCount = scrapy.Field()
    buyStatus = scrapy.Field()
    areaCode = scrapy.Field()
    areaName = scrapy.Field()
    shopcartExist = scrapy.Field()
    quarter = scrapy.Field()
    grade = scrapy.Field()
    gradeName = scrapy.Field()
    shopNum = scrapy.Field()
    orderStatus = scrapy.Field()
    startCourse = scrapy.Field()
    shareUrl = scrapy.Field()
    schoolSwitch = scrapy.Field()
    degreeSwitch = scrapy.Field()
    selfChangeCount = scrapy.Field()
    id = scrapy.Field()
    cityName = scrapy.Field()
    cityCode = scrapy.Field()
    shortCode = scrapy.Field()
    completeSpell = scrapy.Field()
    code = scrapy.Field()
    parentCode = scrapy.Field()
    name = scrapy.Field()
    subject = scrapy.Field()
    crawl_time = scrapy.Field()
    # ----------------
    pageSize = scrapy.Field()
    area = scrapy.Field()
    subjects = scrapy.Field()
    mode = scrapy.Field()
    pageNo = scrapy.Field()
    grade = scrapy.Field()
    quarter = scrapy.Field()


    # ====lesson_info=======
class LebokelessonItem(scrapy.Item):
    no = scrapy.Field()
    name = scrapy.Field()
    beginTime = scrapy.Field()
    endTime = scrapy.Field()
    week = scrapy.Field()
    lessonStatus = scrapy.Field()
    teacherName = scrapy.Field()
    insertBeginLessonNo = scrapy.Field()
    crawl_time = scrapy.Field()
    crawl_flag = scrapy.Field()
    classCode = scrapy.Field()


class LebokeSpeedItem(scrapy.Item):
    classCode = scrapy.Field()
    price = scrapy.Field()
    areaName = scrapy.Field()
    areaCode = scrapy.Field()
    gradeCode = scrapy.Field()
    gradeName = scrapy.Field()
    subjectCode = scrapy.Field()
    subjectName = scrapy.Field()
    beginTime = scrapy.Field()
    endTime = scrapy.Field()
    timeSection = scrapy.Field()
    periodChinese = scrapy.Field()
    childMode = scrapy.Field()
    crawl_time = scrapy.Field()

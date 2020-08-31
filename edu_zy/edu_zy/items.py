# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EduZyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    course_url = scrapy.Field()  #课程url
    course_title = scrapy.Field()  #课程名称
    course_tag = scrapy.Field()  #课程标签(黄色框)
    course_teacher = scrapy.Field()  #课程老师名称
    course_grade = scrapy.Field()  #课程年级
    course_term = scrapy.Field()  #课程学期
    course_nums = scrapy.Field()  #课程讲数
    course_product = scrapy.Field()  #课程产品
    course_campus = scrapy.Field()  #课程校区
    course_tel = scrapy.Field()  #电话
    course_time = scrapy.Field()  #课程时间
    course_address = scrapy.Field()  #地址
    surplusQuota = scrapy.Field()  #配额状态
    claMaterialFee = scrapy.Field()  #物质费
    claFee = scrapy.Field()  #不知道啥费
    claId = scrapy.Field()  #课程ID
    now_price = scrapy.Field()  #现在展示的价格(红色字体-price)
    ori_price = scrapy.Field()  #原价   如果afterDiscountPrice=0，有折扣
    afterDiscountPrice = scrapy.Field()  #折扣标志
    city_name = scrapy.Field()  #城市名称
    city_id = scrapy.Field()    #城市id
    subject_id = scrapy.Field()    #学科ID
    subject_name = scrapy.Field()    #学科名称
    course_id = scrapy.Field()    #课程ID
    course_name = scrapy.Field()    #课程名称
    grade = scrapy.Field()    #年级
    school_id = scrapy.Field()    #学校ID
    crawl_source = scrapy.Field()    #list---现在抓取数据
    batch_time = scrapy.Field()  #批次时间
    crawl_time = scrapy.Field()  #抓取时间

class EduZyCourseBatchItem(scrapy.Item):
    claId = scrapy.Field()  #课程ID
    course_url = scrapy.Field()  #课程url
    course_title = scrapy.Field()  #课程名称
    course_nums = scrapy.Field()  # 课程讲数
    city_name = scrapy.Field()  #城市名称
    city_id = scrapy.Field()    #城市id
    course_batch_time = scrapy.Field()  # 课程课次时间
    batch_time = scrapy.Field()  #批次时间
    crawl_time = scrapy.Field()  #抓取时间
    lesson_num = scrapy.Field()  #课时
    lesson_date = scrapy.Field()  #课时对应的时间
    lesson_value = scrapy.Field()  #对应的时间的原始值

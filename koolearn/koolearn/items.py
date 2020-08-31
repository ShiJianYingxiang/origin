# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class KoolearnItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    class_name = scrapy.Field()
    class_id = scrapy.Field()
    class_type = scrapy.Field()
    class_type_id = scrapy.Field()
    subject = scrapy.Field()
    subject_id = scrapy.Field()
    price = scrapy.Field()
    origin_price = scrapy.Field()
    register_count = scrapy.Field()
    max_count = scrapy.Field()
    start_date = scrapy.Field()
    end_date = scrapy.Field()
    teacher_name = scrapy.Field()
    teacher_id = scrapy.Field()
    teacher_phone = scrapy.Field()
    teacher_type = scrapy.Field()
    teacher_tag = scrapy.Field()
    arrangement = scrapy.Field()
    arrangement_type = scrapy.Field()
    lesson_count = scrapy.Field()
    chapter = scrapy.Field()
    chapter_id = scrapy.Field()
    grade_name = scrapy.Field()
    grade_id = scrapy.Field()
    stage_name = scrapy.Field()
    stage_id = scrapy.Field()
    class_time = scrapy.Field()
    detail_url = scrapy.Field()
    crawl_time = scrapy.Field()
    subClassId = scrapy.Field()
    # -----------教师信息----------------
    class_id = scrapy.Field()
    teacher_name = scrapy.Field()
    teacher_id = scrapy.Field()
    #----------课程信息----------------
    lesson = scrapy.Field()
    temp = scrapy.Field()
    #------------四六级中相关的--------------------
    lesson_name = scrapy.Field()  # 课程名称
    lesson_teacherName = scrapy.Field()  # 授课老师
    lesson_time = scrapy.Field()  # 授课时间


class Koolearn_teacher_Item(scrapy.Item):

    crawl_time = scrapy.Field()
    class_id = scrapy.Field()
    teacher_name = scrapy.Field()
    teacher_id = scrapy.Field()
















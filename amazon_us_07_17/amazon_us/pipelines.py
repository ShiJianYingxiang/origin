# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json
import codecs
import pymongo
import time
import os
from amazon_us.items import AmazonUsCommentItem,AmazonUsItem,AmazonUsProductinfoItem

class AmazonUsPipeline:
    def __init__(self):
        self.filename = codecs.open('/mnt/data/weidong.shi/file/amazon/product_info/product_info_{}_{}.txt'.format(str(os.getpid()),time.strftime('%Y-%m-%d')), 'a+', encoding="utf-8")
        #self.filename1 = codecs.open('product_comment_info.json', 'a+', encoding="utf-8")
        self.filename2 = codecs.open('/mnt/data/weidong.shi/file/amazon/category_to_product/category_to_product_info_{}_{}.json'.format(time.strftime('%Y-%m-%d'),str(os.getpid())), 'a+', encoding="utf-8")
        #self.filename2 = codecs.open('category_to_product_info.json', 'a+', encoding="utf-8")

    def process_item(self, item, spider):
        if isinstance(item, AmazonUsItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.filename.write(text)
            spider.url_db.rpush("amazon_detail_spider:items", 'null')
            #print("{}:items".format(spider.name))
        #if isinstance(item, AmazonUsCommentItem):
        #    text = json.dumps(dict(item), ensure_ascii=False) + "\n"
        #    self.filename1.write(text)
        if isinstance(item, AmazonUsProductinfoItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.filename2.write(text)
            #spider.url_db.rpush("{}:items".format(spider.name), 'null')
            spider.url_db.rpush("amazon_category:info_list_success", 'null')
        return item


    def close_spider(self, spider):
        self.filename.close()
        #self.filename1.close()
        self.filename2.close()

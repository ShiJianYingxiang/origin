# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs, time, os, json
from maidanglao.items import MaidanglaoItem


class MaidanglaoPipeline(object):
    def __init__(self):
        self.filename = codecs.open('/mnt/data/weidong.shi/file/mcdonalds_shops/maidanglao_shop_info_{}_{}.txt'.format(time.strftime('%Y_%m_%d'), os.getpid()), 'a+', encoding='utf-8')


    def process_item(self, item, spider):
        if isinstance(item, MaidanglaoItem):
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.filename.write(text)
        return item


    def close_spider(self, spider):
        self.filename.close()

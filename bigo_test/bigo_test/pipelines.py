# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import time


class BigoTestPipeline(object):
    # def process_item(self, item, spider):
    #     return item
    def __init__(self):
        self.show_filename = codecs.open('/mnt/data/weidong.shi/file/bigo/bigo_show_info_' + time.strftime('%Y-%m-%d %H') + '.txt', 'a+', encoding="utf-8")
        self.game_filename = codecs.open('/mnt/data/weidong.shi/file/bigo/bigo_game_info_' + time.strftime('%Y-%m-%d %H') + '.txt', 'a+', encoding="utf-8")

    def process_item(self, item, spider):
        if spider.name == 'bigo_detail':
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.show_filename.write(text)
            spider.url_db.rpush("bigo_info_spider:show_items", 'null')
        else:
            text = json.dumps(dict(item), ensure_ascii=False) + "\n"
            self.game_filename.write(text)
            spider.url_db.rpush("bigo_info_spider:game_items", 'null')
        return item




    def close_spider(self, spider):
        self.show_filename.close()
        self.game_filename.close()

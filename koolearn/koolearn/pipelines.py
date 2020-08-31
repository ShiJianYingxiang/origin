# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import codecs, json, time

class KoolearnPipeline:
    def __init__(self):
        pass

    def open_spider(self, spider):
        pass

    def process_item(self, item, spider):
        if spider.name == 'koolearn_moblie_teacher':
            file_path = '/mnt/data/weidong.shi/file/kooup_phone_teacher/' + time.strftime('%Y-%m-%d') + '.json'
            with codecs.open(file_path, 'a+', encoding="utf-8") as filename:
                text = json.dumps(dict(item), ensure_ascii=False) + "\n"
                filename.write(text)

        elif spider.name == 'koolearn_mobile':
            file_path = '/mnt/data/weidong.shi/file/kooup_phone_class/' + time.strftime('%Y-%m-%d') + '.json'
            with codecs.open(file_path, 'a+', encoding="utf-8") as filename:
                text = json.dumps(dict(item), ensure_ascii=False) + "\n"
                filename.write(text)

        elif spider.name == 'koolearn_cet4_6':
            file_path = '/mnt/data/weidong.shi/file/koolearn_cet4_6_class/' + time.strftime('%Y-%m-%d') + '.json'
            with codecs.open(file_path, 'a+', encoding="utf-8") as filename:
                text = json.dumps(dict(item), ensure_ascii=False) + "\n"
                filename.write(text)

        elif spider.name == 'koolearn_cet4_6_lessons':
            file_path = '/mnt/data/weidong.shi/file/koolearn_cet4_6_lessons/' + time.strftime('%Y-%m-%d') + '.json'
            with codecs.open(file_path, 'a+', encoding="utf-8") as filename:
                text = json.dumps(dict(item), ensure_ascii=False) + "\n"
                filename.write(text)

        elif spider.name == 'koolearn_cet4_6_teacher':
            file_path = '/mnt/data/weidong.shi/file/koolearn_cet4_6_teacher/' + time.strftime('%Y-%m-%d') + '.json'

            with codecs.open(file_path, 'a+', encoding="utf-8") as filename:
                text = json.dumps(dict(item), ensure_ascii=False) + "\n"
                filename.write(text)

        return item


    def close_spider(self, spider):
        pass


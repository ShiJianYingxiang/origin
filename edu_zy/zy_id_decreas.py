# coding=utf-8
from scrapy import cmdline


def generate_spider_cmd(name):
    cmd = "scrapy crawl {name}".format(name=name)
    return cmd


def main():


    print("卓越教育爬虫ID递减副本开启------------------")
    cmdline.execute(generate_spider_cmd("course_id_decreas").split())

# ershou_viewer
if __name__ == "__main__":
    main()

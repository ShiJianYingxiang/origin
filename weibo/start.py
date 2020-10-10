# coding=utf-8
from scrapy import cmdline


def generate_spider_cmd(name):
    cmd = "scrapy crawl {name}".format(name=name)
    return cmd


def main():
    print("微博抓取")
    cmdline.execute(generate_spider_cmd("weibo_spider").split())


# ershou_viewer
if __name__ == "__main__":
    main()
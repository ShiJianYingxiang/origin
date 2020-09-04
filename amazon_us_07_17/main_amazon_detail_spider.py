# coding=utf-8
from scrapy import cmdline


def generate_spider_cmd(name):
    cmd = "scrapy crawl {name}".format(name=name)
    return cmd


def main():
    print("亚马逊商品详情的程序已经启动。")
    cmdline.execute(generate_spider_cmd("amazon_spider_detail").split())


if __name__ == "__main__":
    main()

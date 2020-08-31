# coding=utf-8
from scrapy import cmdline


def generate_spider_cmd(name):
    cmd = "scrapy crawl {name}".format(name=name)
    return cmd


def main():
    #print("贝壳地方排行榜")
    #cmdline.execute(generate_spider_cmd("get_cities_rank").split())

    print("二手房带看人次")
    cmdline.execute(generate_spider_cmd("ershou_viewer").split())

# ershou_viewer
if __name__ == "__main__":
    main()

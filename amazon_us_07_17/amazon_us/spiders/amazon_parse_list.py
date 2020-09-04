# -*- coding: utf-8 -*-
import scrapy
import redis
import re
import json
import os
import time
from amazon_us.items import AmazonUsProductinfoItem

class CategoryGetDetailSpider(scrapy.Spider):
    name = 'amazon_list_spider'
    # start_urls = ['https://www.amazon.com/']
    headers = {
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "zh-CN,zh;q=0.9",
        "cache-control": "no-cache",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "pragma": "no-cache",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'amazon_list_spider'
    comment_second_url = "https://www.amazon.com/s?bbn={}&rh={}&s=review-rank&dc&ref=sr_ex_n_1"
    second_url = "https://www.amazon.com/s?bbn={}&rh={}&s=featured-rank&dc&ref=sr_ex_n_1"
    detail_name = 'amazon_detail_spider'

    def start_requests(self):
        while 1:
            #更新了弹出的key---分类信息
            body = self.url_db.lpop("amazon_category:info_list")
            if body:
                if isinstance(body, bytes):
                    body = body.decode()
                content = json.loads(body)
                number = 1
                category_list = []
                for keys in content.keys():
                    if "name" not in keys:
                        category_list.append("n:" + str(content['c{}'.format(number)]))
                        number += 1
                c_count = ",".join(category_list)
                selector_url = self.second_url.format(content.get('c1'), c_count)
                comment_url = self.comment_second_url.format(content.get('c1'), c_count)
                yield scrapy.Request(url=selector_url, headers=self.headers, meta={'category_info': json.dumps(content)},callback=self.parse)
                yield scrapy.Request(url=comment_url, headers=self.headers, meta={'category_info': json.dumps(content)},callback=self.parse)
                self.logger.info("爬取链接是{}".format(comment_url))
                self.logger.info('{}分类开始爬取'.format(content))
            else:
                self.logger.info("程序完成, 退出！")
                break


    def parse(self, response):
        category_info = response.meta.get('category_info', '')   #获取传递下来的分类信息
        self.logger.info("{}开始抓取类别,准备翻页".format(category_info))

        if 'Robot Check' in response.text:
            self.logger.info('-----------Robot Check----------出现了')
            self.url_db.lpush('amazon_category:info_list_failed', response.url)
            return
        total_page_number = response.xpath('''(//ul[@class="a-pagination"]//li)[last()-1]/text()|(//ul[@class="a-pagination"]//li)[last()-1]/a/text()''').get()   #获取总的页数

        if not total_page_number:
            self.logger.info('-----链接:{}----没有翻页页数---ERROR----'.format(response.url))
            self.url_db.lpush('amazon_category:info_list_failed', response.url)
            yield scrapy.Request(url=response.url, headers=self.headers, meta={'category_info': category_info, 'total_page_number':'1', 'now_page': '1'}, callback=self.get_all_product)
        else:
            self.logger.info('=======分类{}====总页数是{}========='.format(category_info, total_page_number))
            for item in range(1, int(total_page_number)+1):
                next_page_url = response.url + '&page=' + str(item)
                yield scrapy.Request(url=next_page_url, headers=self.headers, meta={'category_info': category_info, 'total_page_number':str(total_page_number), 'now_page': str(item)}, callback=self.get_all_product)

        # url = 'https://www.amazon.com/s?bbn=2619525011&rh=n:2619525011,n:3741181,n:2232343011&s=featured-rank&dc&ref=sr_ex_n_1&page=55'
        # yield scrapy.Request(url=url, headers=self.headers,
        #                      meta={'category_info': 'category_info', 'total_page_number': 11,
        #                            'now_page': 11}, callback=self.get_all_product)


    def get_all_product(self, response):
        now_page = response.meta.get('now_page', '')                     #获取当前页数
        total_page_number = response.meta.get('total_page_number', '')   #获取总页数
        category_info = response.meta.get('category_info', '')           #获取传递下来的分类信息
        self.logger.info('当前是{}分类下---总共有{}页---现在是在第{}页'.format(category_info, total_page_number, now_page))

        country = response.xpath('''(//div[@id="glow-ingress-block"]//span)[2]/text()''').extract()[0].strip()
        self.logger.info('====This is {}=========='.format(country))

        if 'featured-rank' in response.url:
            comment_flag = '精选'
        else:
            comment_flag = '评论'
        #对列表页中的每一个商品进行解析，
        productid_list = response.xpath('''//div[@class="a-section a-spacing-medium"]''')#.getall()
        now_page_productid_num = str(len(productid_list))     #当前页面内有多少商品数

        if not productid_list:
            self.logger.info('-----链接:{}---第{}页无展示商品--------'.format(response.url, now_page))
            return
        else:
            item = AmazonUsProductinfoItem()
            category_info = json.loads(category_info)
            item.update(category_info)

        for product_temp in productid_list:
            productID_comments_content = product_temp.xpath('''.//div[@class="a-row a-size-small"]/span[1]/@aria-label''').get()  # 获取商品评论内容
            # if not productID_comments_content:
            #     continue
            # comment_star = re.search('(.*?)\s*out', productID_comments_content).group(1)
            # if comment_star < '4.0':   #星级数小于4.0的过滤掉
            #     continue

            productID_comments_nums = product_temp.xpath('''.//div[@class="a-row a-size-small"]/span[2]//span[@class="a-size-base"]/text()''').get()  # 获取商品评论数
            # if not productID_comments_nums:
            #     continue
            # if int(productID_comments_nums) < 50:  #评论数小于50的过滤掉
            #     continue

            product_href = product_temp.xpath('''.//h2//a/@href''').get()  #获取商品链接
            productID = re.findall(r'dp/(\w{10})/', product_href)
            productID = productID[0] if productID else None
            if not productID:
                continue

            item['productID'] = productID                                     #商品id
            if not self.url_db.sismember("amazon_category:product_set", productID):
                self.url_db.sadd("amazon_category:product_set", productID)
                self.url_db.lpush("amazon_category:product_list", productID)
            item['now_page'] = now_page                                       #该商品所在的页面数
            item['total_page_number'] = total_page_number                     #该商品分类下总的页面数
            item['category_info'] = category_info                             #获取传递下来的分类信息
            item['now_page_productid_num'] = now_page_productid_num           #当前页面内有多少商品数
            item['comment_featured'] = comment_flag                               #来自评论还是精选
            item['batch'] = '2020-09-04'                       #批次
            item['ctime'] = time.strftime('%Y-%m-%d %H:%M:%S')
            item['productID_comments_nums'] = productID_comments_nums         #商品的评论数
            item['productID_comments_content'] = productID_comments_content   #商品的评论内容
            # self.logger.info(item)
            yield item







# -*- coding: utf-8 -*-
'''
解析详情页
(获取商品的url是去重过后的)
eg:
https://www.amazon.com/dp/B07ZQCST89/
https://www.amazon.com/dp/B07Z8TC28F/

解析获取的详情页
    shop_url进行存储,去重---(扩展数据源)


'''
import scrapy
import re
import time
from urllib.parse import urljoin
import redis
import json
from lxml import etree
import copy
import os
from amazon_us.items import AmazonUsItem
#from scrapy.utils.markup import remove_tags, remove_tags_with_content
#from scrapy.utils.markup import remove_tags

class AmazonSpiderSpider(scrapy.Spider):
    name = 'amazon_spider_detail'
    # allowed_domains = ['amazon.com']
    # start_urls = ['https://www.amazon.com/dp/B07Z8TC28F/']
    headers = {
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "sec-fetch-site": "none",
        "sec-fetch-mode": "navigate",
        "sec-fetch-user": "?1",
        "sec-fetch-dest": "document",
        "accept-encoding": "gzip, deflate, br",
    }
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'swd_amazon'
    swd_amazon_shop_set = "{}:shop_set".format(base_key)
    swd_amazon_shop_list = "{}:shop_list".format(base_key)
    swd_amazon_product_list = 'amazon_detail_spider:start_urls'      #存放分类下的所有商品ID----list
    category_detail_set = "{}:category_detail_set".format(base_key)         #存放详情发现的category----set
    category_detail_list = "{}:category_detail_list".format(base_key)       #存放详情发现的category----list
    detail_error = "{}:detail_error_set".format(base_key)     #记录没有价格的商品ID
    # swd_amazon: all_productid_set
    swd_amazon_product_set = '{}:all_productid_set'.format(base_key)      #存放分类下的所有商品ID----set
    item = AmazonUsItem()

    def clear_special_xp(self, data, xp):
        data = copy.copy(data)
        result = data.xpath(xp)
        for i in result:
            try:
                i.getparent().remove(i)
            except Exception as e:
                print(e)
        return data

    def start_requests(self):
        while 1:
            redis_dict = self.url_db.lpop(self.swd_amazon_product_list)   #
            if redis_dict:
                if isinstance(redis_dict, bytes):
                    product_id = redis_dict.decode()
                product_url = 'http://www.amazon.com/dp/{}/'.format(product_id)
                yield scrapy.Request(url=product_url, headers=self.headers, meta={'product_id':product_id}, callback=self.parse)   #,dont_filter=True
            else:
                self.logger.info('程序已完成，退出！！！')
                break


    def parse(self, response):
        #        pass

        self.logger.info('-----开始抓取商品详情-------')
        productID = re.findall(r'/(\w{10})', response.url)
        pid = productID[0] if productID else None  # 商品唯一标识
        if not pid:
            self.logger.error('没有找到商品ID')
        url = 'https://www.amazon.com/dp/{}/'.format(pid)  # 商品链接
        source = 'amazon'  # 网站来源

        with open('/mnt/data/weidong.shi/file/amazon/html/{}.html'.format(str(os.getpid())), 'a+', encoding='utf-8') as ee:
            ee.write(response.text.replace('\n', '') + '\n')
        # with open('{}.html'.format(str(os.getpid())), 'a+', encoding='utf-8') as ee:
        #     ee.write(response.text.replace('\n', '') + '\n')


        category_list = response.xpath('''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]/text()''').getall()
        category = [x.replace('\n', '').replace(' ', '').strip() for x in category_list]  # 导航列表
        new_category = ">".join(category)  # ca

        category_id_list = []  # 导航列表的值
        breadcrumb_url_list = response.xpath('''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]//@href''').getall()
        for item in breadcrumb_url_list:
            breadcrumb_url = item.replace('\n', '').replace(' ', '').strip()
            if '&rh=' in breadcrumb_url:
                breadcrumb_id = re.search(r'&rh=(.*?)&', breadcrumb_url).group(1)
                category_id_list.append(breadcrumb_id)
            elif '&node=' in breadcrumb_url:
                breadcrumb_id = re.search(r'&node=(\d+)', breadcrumb_url).group(1)
                category_id_list.append(breadcrumb_id)

        index = 0
        category_tree = dict()
        for l in range(len(category)):
            category_tree['category{}'.format(index + 1)] = category[l]
            category_tree['category{}_id'.format(index + 1)] = category_id_list[l]
            index += 1

        title_content = response.xpath('''//title/text()''').get()
        title_content1 = title_content.replace('\n', '').replace('Amazon.com: ', '')
        try:
            title = title_content1.split(':')[0]
        except:
            title = title_content1
        if 'Robot Check' in title:
            self.logger.error('======Robot Check出现了========{}=========='.format(pid))
            self.url_db.rpush('amazon_detail_spider:robot_check', pid)
            return
        # 品牌名
        brand_name = response.xpath('''//a[@id="bylineInfo"]/text()''').get()

        shop_url = response.xpath('''//a[@id="bylineInfo"]/@href''').get()
        if shop_url:
            if 'http' not in shop_url:
                shop_url = 'https://www.amazon.com' + shop_url
            else:
                shop_url = ''

        # 商品评分/好评率
        if 'acrPopover' in response.text:
            star_score_content = response.xpath('''(//span[@id="acrPopover"])[1]//@title''').get()
            if star_score_content:
                if 'out' in star_score_content:
                    score = star_score_content.split('out')[0].strip()
                else:
                    score = ''
                    self.logger.error('------score_xpath错误---{}---------')
            comments_num_content = response.xpath('''(//a[@id="acrCustomerReviewLink"]//span[@id="acrCustomerReviewText"])[1]/text()''').get()
            if comments_num_content:
                comment_count = comments_num_content.replace('ratings', '').strip()
        else:
            score = ''
            comment_count = 0
            self.logger.info('======={}没有评论==============='.format(pid))

        # 各个星级对应的比例
        star_level = response.xpath('''//table[@id="histogramTable"]//tr//td[1]//a/text()''').getall()
        star_proportion = response.xpath('''//table[@id="histogramTable"]//tr//td[3]//a/text()''').getall()
        star_dict = dict()
        for x, y in zip(star_level, star_proportion):
            x = x.strip()
            y = y.strip()
            star_dict[x] = y

        crawler_tm = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))  # 采集时间  #采集时间===========================
        # 图片
        images_content = response.xpath('''//div[@id="altImages"]//ul//li//img//@src''').getall()
        images = [x.strip() for x in images_content]

        summary_content = dict()
        summary_key_list = response.xpath(
            '''//table[@id="productDetails_techSpec_section_1"]//tr/th/text()''').getall()
        summary_value_list = response.xpath(
            '''//table[@id="productDetails_techSpec_section_1"]//tr/td/text()''').getall()
        for key, value in zip(summary_key_list, summary_value_list):
            key = key.strip()
            value = value.strip()
            summary_content[key] = value
        # print(summary_content,'11111111111111111111')
        # ---------------------------------------------------------

        content = etree.HTML(response.text)
        content = self.clear_special_xp(content, '//style|//script')

        try:
            if 'Currently unavailable' in response.text or 'Available from' in response.text:
                price = ''  # 无货
                sale_status = 2
            else:
                price = content.xpath('''//div[@id="buyNew_noncbb"]//span/text()|//div[@id="cerberus-data-metrics"]//@data-asin-price|//div[@id="price"]//span[@id="priceblock_ourprice"]/text()|//span[@id="price_inside_buybox"]/text()''')[0]
                sale_status = 1
        except:
            self.logger.error('@@@@@@价格有问题{}@@@@@@@@@@@@@@@'.format(pid))
            price = 'error'
            sale_status = 0
        if price == 'error' or not price:
            price = price
        else:
            if '$' not in price:
                price = '$' + price

        # 添加bsr    B00WEYVE5U|B00WEYVE5U
        other_style_list = content.xpath('''//li[@id="SalesRank"]''')
        for item in other_style_list:
            style_key = item.xpath('''./b/text()''')[0]
            style_key = style_key.replace('Amazon', '').replace(' ', '').replace(':', '')
            style_value = item.xpath('''./text()|./a/text()''')
            style_value1 = ''
            for i in style_value:
                style_value1 += i.strip()
            summary_content[style_key] = style_value1

        # -------添加其他参数------------
        other_dict = dict()
        other_style_list1 = content.xpath(
            '''//div[@id="descriptionAndDetails"]//div[@id="detailBullets_feature_div"]//ul//li''')
        for item1 in other_style_list1:
            item_key_list = item1.xpath('''.//span[@class="a-list-item"]/span[@class="a-text-bold"]/text()''')
            item_value_list = item1.xpath('''(.//span[@class="a-list-item"]/span)[2]/text()''')
            for item_key, item_value in zip(item_key_list, item_value_list):
                if not item_key:
                    continue
                else:
                    other_dict[item_key] = item_value
        summary_content.update(other_dict)
        sellers_rank = dict()
        list_ = content.xpath(
            '//table[@id="productDetails_detailBullets_sections1"]//tr|//table[@id="product-specification-table"]//tr')
        for item in list_:
            key = item.xpath('''./th/text()''')
            value = item.xpath('''./td//text()''')
            zz = list()
            xx = ''
            for value_temp in value:
                xx += value_temp.replace('\n', '')
            zz.append(xx)
            for k, v in zip(key, zz):
                k = k.replace('\n', '').replace(' ', '')
                sellers_rank[k] = v

        # print(sellers_rank, '===========222222222222222============')

        summary_content.update(sellers_rank)

        if 'Sellers Rank' in response.text:
            if 'BestSellersRank' in summary_content.keys():
                bsr = summary_content.get('BestSellersRank', '')
            else:
                bsr = ''
                print('BestSellersRank没抓取到----{}'.format(pid))
        else:
            bsr = '-1'
            self.url_db.rpush('amazon_detail_spider:no_bsr', pid)
            self.logger.info('----{}----没有BestSellersRank'.format(pid))

        shop_id = ''  # 店铺id
        shop_starts = ''  # 开店时间
        shop_name = ''  # 店铺名字
        shop_evaluates = ''  # 店铺评分
        shop_credi_level = ''  # 店铺等级
        ori_price = ''  # 原价
        descibe = ''  # 商品详细描述
        descibe_more = ''  # 商品更多信息
        sku_list = ''  # sku商品列表
        brand_id = ''  #品牌id
        batch_tm = time.strftime('%Y-%m-%d %H') + ':00:00'  #批次时间
        # 未找到的字段
        sku_id = ''
        spu_id = ''  #
        model = ''  # 款式参数
        support = ''  # 是否自营
        sales_count = ''  # 总销量
        sales_count_month = ''  # 月销量
        praise_count = ''  # 好评数
        medium_count = ''  # 中评数
        bad_count = ''  # 差评数
        storage_count = ''  # 库存数
        collection_count = ''  # 收藏/关注数
        delivery_from = ''  # 发货地
        presell_count = ''  # 预售量
        presell_price = ''  # 预售价
        goods_types = ''  # 标签
        promo_list = ''  # 优惠信息
        subtitle = ''  # 副标题
        self.item['pid'] = pid
        self.item['sku_id'] = sku_id
        self.item['spu_id'] = spu_id
        self.item['url'] = url
        self.item['sale_status'] = sale_status
        self.item['source'] = source
        self.item['category'] = new_category
        self.item['title'] = title
        self.item['brand_id'] = brand_id
        self.item['brand_name'] = brand_name
        self.item['model'] = summary_content   ##############
        self.item['price'] = price
        self.item['ori_price'] = ori_price
        self.item['support'] = support
        self.item['shop_id'] = shop_id
        self.item['shop_starts'] = shop_starts
        self.item['shop_name'] = shop_name
        self.item['shop_evaluates'] = shop_evaluates
        self.item['shop_credi_level'] = shop_credi_level
        self.item['score'] = score
        self.item['descibe'] = descibe
        self.item['descibe_more'] = descibe_more
        self.item['sku_list'] = sku_list
        self.item['sales_count'] = sales_count
        self.item['sales_count_month'] = sales_count_month
        self.item['comment_count'] = comment_count
        self.item['praise_count'] = praise_count
        self.item['medium_count'] = star_dict   #####################
        self.item['bad_count'] = bad_count
        self.item['storage_count'] = storage_count
        self.item['collection_count'] = collection_count
        self.item['delivery_from'] = delivery_from
        self.item['batch_tm'] = batch_tm
        self.item['crawler_tm'] = crawler_tm
        self.item['presell_count'] = presell_count
        self.item['presell_price'] = presell_price
        self.item['goods_types'] = goods_types
        self.item['promo_list'] = promo_list
        self.item['images'] = images
        self.item['subtitle'] = subtitle
        self.item['bsr'] = bsr
        self.item.update(category_tree)
        # self.logger.info('******{}商品详情抓取完成************'.format(pid))
        yield self.item
        # with open('/mnt/data/weidong.shi/file/amazon/product_info/product_detail_info.json', 'a+', encoding='utf-8') as e:
        # with open('product_detail_info.json', 'a+', encoding='utf-8') as e:
        #    e.write(json.dumps(self.item) + '\n')

# -*- coding: utf-8 -*-
import scrapy
import re
import time
import redis
import json
from amazon_us.items import AmazonUsItem

class TestSpider(scrapy.Spider):
    name = 'test'
    #allowed_domains = ['amazon.com']
    #start_urls = ['http://amazon.com/']

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en',
        'Accept-Encoding': 'gzip,deflate',
        #'cookie': 'session-id=144-5953255-9071136; session-id-time=2082787201l; i18n-prefs=USD; ubid-main=133-0153621-7443973; x-wl-uid=1I1PQHoyVu5ada5B/v/7AT833uM2rOxApPjzm7ppaojiyvyCiB75bgP5BE2dczX67ehPfOx3VtX8=; lc-main=en_US; session-token=0ccSiAbm9IfRr3eWN0rj+TV1KQkQc1vBFY5kYsmiBA3TNY4Sc+MxLgbRdx90b2No8tzph+qycXn6Q1S9REAMjbkpjLBo0yf6Ofrq0CI9NZtrJwR7w9BJeUM7ypXgfk+B9Y5750OSzSLK5yRGz1dcUDnUQ/jp7mOh/VV6lMdX+KGfj2XpX3zV8bHZrB2VOiAF; csm-hit=tb:BBKT1KW6NQ0FSG3B20VG+sa-VWXMRGHPZQASQASS14CD-R0R6GD7X2Q2WW5NXHC7B|1594478673964&t:1594478673964&adb:adblk_no',
        
    }
    try:
        url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
    except:
        url_db = None
    base_key = 'swd_amazon'
    swd_amazon_shop_set = "{}:shop_set".format(base_key)
    swd_amazon_shop_list = "{}:shop_list".format(base_key)
    swd_amazon_product_list = '{}:all_productid_list'.format(base_key)      #存放分类下的所有商品ID----list
    category_detail_set = "{}:category_detail_set".format(base_key)         #存放详情发现的category----set
    category_detail_list = "{}:category_detail_list".format(base_key)       #存放详情发现的category----list
    detail_error = "{}:detail_error_set".format(base_key)     #记录没有价格的商品ID
    item = dict()#AmazonUsItem()

    def start_requests(self):
       # str_len = self.url_db.llen(self.swd_amazon_product_list)
       # for i in range(str_len):
       #     redis_dict = self.url_db.rpoplpush(self.swd_amazon_product_list, self.swd_amazon_product_list)   #
       #     if isinstance(redis_dict, bytes):
       #         product_id = redis_dict.decode()
       #     product_url = 'https://www.amazon.com/dp/{}/'.format(product_id)
       #     yield scrapy.Request(url=product_url, headers=self.headers, callback=self.parse)
        product_id = 'B07WP34LNQ'
        product_url = 'https://www.amazon.com/dp/{}'.format(product_id)
        print(product_url)
        yield scrapy.Request(url=product_url, headers=self.headers, callback=self.parse)

    def parse(self, response):
#        pass
        productID = re.findall(r'/(\w{10})', response.url)
        pid = productID[0] if productID else None     #商品唯一标识
        if not pid:
            self.logger.error('没有找到商品ID')
        print(pid)
        print(response.text)
        other_technical_list = response.xpath('''//table[@id="productDetails_detailBullets_sections1"]//tr''')
        for detail_item in other_technical_list:
            seller2 = detail_item.xpath('''./th/text()''')
            seller_value1 = detail_item.xpath('''./td/text()|./td//span/text()|./td//span//a/text()''')
            print(seller2, '---------------', seller_value1)
            #print(type(seller2),'===============', type(seller_value1))



        ware_url = 'https://www.amazon.com/dp/{}/'.format(pid)   #商品链接
        sale_status = 1  #售卖状态
        source = 'amazon'       #网站来源
        breadcrumb = response.xpath('''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]/text()''').getall()
        category = [x.replace('\n', '').replace(' ', '').strip() for x in breadcrumb]
        print(category)
        category_id_list = []
        breadcrumb_url_list = response.xpath('''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]//@href''').getall()
        for item in breadcrumb_url_list:
            breadcrumb_url = item.replace('\n', '').replace(' ', '').strip()
            if '&rh=' in breadcrumb_url:
                breadcrumb_id = re.search(r'&rh=(.*?)&', breadcrumb_url).group(1)
                category_id_list.append(breadcrumb_id)
            elif '&node=' in breadcrumb_url:
                breadcrumb_id = re.search(r'&node=(\d+)', breadcrumb_url).group(1)
                category_id_list.append(breadcrumb_id)

        category_tree = dict()
        for category_key, category_id_value in zip(category,category_id_list):
            category_tree[category_key] = category_id_value

        category_tree_content = json.dumps(category_tree)
		#存放详情发现的category列表
        if not self.url_db.sismember(self.category_detail_set, category_tree_content):
            self.url_db.sadd(self.category_detail_set, category_tree_content)
            self.url_db.lpush(self.category_detail_list, category_tree_content)

        title = response.xpath('''//span[@id="productTitle"]/text()''').get()
        if not title:
            self.logger.error('-------no_title{}--------------'.format(pid))
		#品牌ID
        brand_id = ''
		#品牌name
        brand_name = response.xpath('''//a[@id="bylineInfo"]/text()''').get()
		# 店铺url
        shop_url = response.xpath('''//a[@id="bylineInfo"]/@href''').get()
        if shop_url:
            if 'http' not in shop_url:
                shop_url = 'https://www.amazon.com' + shop_url
            else:
                shop_url = ''
		# 价格
        price = response.xpath('''//div[@id="price"]//span[@id='priceblock_ourprice']/text()|//div[@id="cerberus-data-metrics"]/@data-asin-price''').get()   #//span[@id='priceblock_ourprice']/text()|
		# print(price, '----------price----11-------')
        if not price:
            price = response.xpath('''//div[@id="buyNew_noncbb"]//span/text()''').get()
            if not price:
                self.url_db.sadd(self.detail_error, pid)

        ori_price = response.xpath('''//span[contains(@class,"priceBlockStrikePriceString")]/text()''').get()
        if not ori_price:
            ori_price = price
        shop_id = ''      # 店铺id
        shop_starts = ''  #开店时间
        shop_name = ''    #店铺名字
        shop_evaluates = ''   #店铺评分
        shop_credi_level = ''   #店铺等级

        # 商品评分/好评率
        score = ''
        star_score_content = response.xpath('''//span[@class="a-size-base a-nowrap"]//span/text()''').get()
        if star_score_content:
            if 'out' in star_score_content:
                score = star_score_content.split('out')[0].strip()
            else:
                score = ''
                self.logger.error('------score_xpath错误---{}---------'.format(pid))
        # 各个星级对应的比例
        star_level = response.xpath('''//table[@id="histogramTable"]//tr//td[1]//a/text()''').getall()
        star_proportion = response.xpath('''//table[@id="histogramTable"]//tr//td[3]//a/text()''').getall()
        star_dict = dict()
        for x, y in zip(star_level, star_proportion):
            x = x.strip()
            y = y.strip()
            star_dict[x] = y

        descibe = ''     #商品详细描述
        descibe_more = ''  #商品更多信息
        sku_list = ''    #sku商品列表
        # 评论数
        comment_count = ''
        comments_num_content = response.xpath('''(//a[@id="acrCustomerReviewLink"]//span[@id="acrCustomerReviewText"])[1]/text()''').get()
        if comments_num_content:
            comment_count = comments_num_content.replace('ratings', '').strip()
        batch_tm = ''     #批次时间
        crawler_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))    #采集时间
		#图片
        images_content = response.xpath('''//div[@id="altImages"]//ul//li//img//@src''').getall()
        images = [x.strip() for x in images_content]

        #参数  //table[@id="productDetails_detailBullets_sections1"]
        summary_key_list = response.xpath('''//table[@id="productDetails_techSpec_section_1"]//tr/th/text()''').getall()
        summary_value_list = response.xpath('''//table[@id="productDetails_techSpec_section_1"]//tr/td/text()''').getall()
        summary_content = dict()
        for key, value in zip(summary_key_list, summary_value_list):
            key = key.strip()
            value = value.strip()
            summary_content[key] = value
        #排名参数
        other_technical_detail = dict()
        technical_key_list = response.xpath('''//table[@id="productDetails_detailBullets_sections1"]//tr/th/text()''').getall()
        technical_value_list = response.xpath('''//table[@id="productDetails_detailBullets_sections1"]//tr//td/text()''').getall()

        for technical_key, technical_value in zip(technical_key_list, technical_value_list):
            technical_key = technical_key.strip()
            technical_value = technical_value.strip()
            other_technical_detail[technical_key] = technical_value


        other_technical_list = response.xpath('''//table[@id="productDetails_detailBullets_sections1"]//tr''')
        for detail_item in other_technical_list:
            seller2 = detail_item.xpath('''./th/text()''')
            seller_value1 = detail_item.xpath('''./td/text()|./td//span/text()|./td//span//a/text()''')
            print(seller2, '---------------', seller_value1)        



        # 未找到的字段
        sku_id = ''
        spu_id = ''            #
        model = ''             #款式参数
        support = ''           #是否自营
        sales_count = ''       #总销量
        sales_count_month = ''       #月销量
        praise_count = ''       #好评数
        medium_count = ''       #中评数
        bad_count = ''          #差评数
        storage_count = ''      #库存数
        collection_count = ''   #收藏/关注数
        delivery_from = ''      #发货地
        presell_count = ''      #预售量
        presell_price = ''      #预售价
        goods_types = ''        #标签
        promo_list = ''         #优惠信息
        subtitle = ''           #副标题



        self.item['pid'] = pid
        self.item['ware_url'] = ware_url
        self.item['sale_status'] = sale_status
        self.item['source'] = source
        self.item['category'] = category
        self.item['category_id_list'] = category_id_list
        self.item['category_tree'] = category_tree
        self.item['title'] = title
        self.item['brand_id'] = brand_id
        self.item['brand_name'] = brand_name
        self.item['price'] = price
        self.item['ori_price'] = ori_price
        self.item['shop_id'] = shop_id
        self.item['shop_starts'] = shop_starts
        self.item['shop_name'] = shop_name
        self.item['shop_evaluates'] = shop_evaluates
        self.item['shop_credi_level'] = shop_credi_level
        self.item['shop_url'] = shop_url
        self.item['score'] = score
        self.item['star_dict'] = star_dict
        self.item['descibe'] = descibe
        self.item['descibe_more'] = descibe_more
        self.item['sku_list'] = sku_list
        self.item['comment_count'] = comment_count
        self.item['batch_tm'] = batch_tm
        self.item['crawler_tm'] = crawler_tm
        self.item['images'] = images
        self.item['summary_content'] = summary_content
        self.item['other_technical_detail'] = other_technical_detail
        self.item['sku_id'] = sku_id
        self.item['spu_id'] = spu_id
        self.item['model'] = model
        self.item['support'] = support
        self.item['sales_count'] = sales_count
        self.item['sales_count_month'] = sales_count_month
        self.item['praise_count'] = praise_count
        self.item['medium_count'] = medium_count
        self.item['bad_count'] = bad_count
        self.item['storage_count'] = storage_count
        self.item['collection_count'] = collection_count
        self.item['delivery_from'] = delivery_from
        self.item['presell_count'] = presell_count
        self.item['presell_price'] = presell_price
        self.item['goods_types'] = goods_types
        self.item['promo_list'] = promo_list
        self.item['subtitle'] = subtitle
        #with open('product_detail_info.json', 'a+', encoding='utf-8') as e:
        #    e.write(json.dumps(self.item) + '\n')

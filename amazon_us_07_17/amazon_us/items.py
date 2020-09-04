# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonUsItem(scrapy.Item):
    # define the fields for your item here like:
    pid = scrapy.Field()            #商品唯一标识
    sku_id = scrapy.Field()
    spu_id = scrapy.Field()            #
    url = scrapy.Field()       #商品链接
    sale_status = scrapy.Field()    #售卖状态
    source = scrapy.Field()         #网站来源
    category = scrapy.Field()       #目录名称列表
    title = scrapy.Field()        #商品标题
    brand_id = scrapy.Field()     #品牌ID
    brand_name = scrapy.Field()   #品牌name
    model = scrapy.Field()             #款式参数
    price = scrapy.Field()        #价格
    ori_price = scrapy.Field()    #原价
    support = scrapy.Field()           #是否自营
    shop_id = scrapy.Field()      # 店铺id
    shop_starts = scrapy.Field()  # 开店时间
    shop_name = scrapy.Field()    # 店铺名字
    shop_evaluates = scrapy.Field()  # 店铺评分
    shop_credi_level = scrapy.Field()  # 店铺等级
    score = scrapy.Field()        #商品得分
    descibe = scrapy.Field()  # 商品详细描述
    descibe_more = scrapy.Field()  # 商品更多信息
    sku_list = scrapy.Field()  # sku商品列表
    sales_count = scrapy.Field()       #总销量
    sales_count_month = scrapy.Field()  #月销量
    comment_count = scrapy.Field()  #对应评论数
    praise_count = scrapy.Field()       #好评数
    medium_count = scrapy.Field()       #中评数
    bad_count = scrapy.Field()          #差评数
    storage_count = scrapy.Field()      #库存数
    collection_count = scrapy.Field()   #收藏/关注数
    delivery_from = scrapy.Field()      #发货地
    batch_tm = scrapy.Field()       #批次时间
    crawler_tm = scrapy.Field()     #抓取时间
    presell_count = scrapy.Field()      #预售量
    presell_price = scrapy.Field()      #预售价
    goods_types = scrapy.Field()        #标签
    promo_list = scrapy.Field()         #优惠信息
    images = scrapy.Field()       #商品图片
    subtitle = scrapy.Field()           #副标题
    bsr = scrapy.Field()   #bsr
    category1 = scrapy.Field()
    category1_id = scrapy.Field()
    category2 = scrapy.Field()
    category2_id = scrapy.Field()
    category3 = scrapy.Field()
    category3_id = scrapy.Field()
    category4 = scrapy.Field()
    category4_id = scrapy.Field()
    category5 = scrapy.Field()
    category5_id = scrapy.Field()
    category6 = scrapy.Field()
    category6_id = scrapy.Field()
    category7 = scrapy.Field()
    category7_id = scrapy.Field()

class AmazonUsProductinfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    productID = scrapy.Field()    #商品ID
    now_page = scrapy.Field()     #该商品所在的页面数
    total_page_number = scrapy.Field()   #该商品分类下总的页面数
    category_info = scrapy.Field()    #获取传递下来的分类信息
    now_page_productid_num = scrapy.Field()       #当前页面内有多少商品数
    comment_featured = scrapy.Field()          #来自评论还是精选
    productID_comments_nums = scrapy.Field()          #商品的评论数
    productID_comments_content = scrapy.Field()          #商品的评论内容
    c1 = scrapy.Field()
    c1_name = scrapy.Field()
    c2 = scrapy.Field()
    c2_name = scrapy.Field()
    c3 = scrapy.Field()
    c3_name = scrapy.Field()
    c4 = scrapy.Field()
    c4_name = scrapy.Field()
    c5 = scrapy.Field()
    c5_name = scrapy.Field()
    c6 = scrapy.Field()
    c6_name = scrapy.Field()
    ctime = scrapy.Field()
    batch = scrapy.Field()
    c7 = scrapy.Field()
    c7_name = scrapy.Field()
    



class AmazonUsCommentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_url = scrapy.Field()    #商品url
    comment_count = scrapy.Field()  #评论数
    comment_time = scrapy.Field()   #评论时间
    user_avatar = scrapy.Field()    #评论用户头像
    user_url = scrapy.Field()       #评论用户url
    score = scrapy.Field()          #评论评分
    title = scrapy.Field()          #评论标题
    content = scrapy.Field()        #评论内容
    images = scrapy.Field()         #评论中图片
    product_description = scrapy.Field()  #具体购买的商品信息
    up_count = scrapy.Field()         #别人觉得评论有用数
    comment_id = scrapy.Field()       #评论id
    commentid_url = scrapy.Field()    #评论展示url






# coding:utf-8
import gevent
from gevent import monkey, pool

monkey.patch_all()
import sys
import traceback
import requests
import re
import time
import json
import copy
import datetime
from lxml import etree
import redis
import os
'''
对通过bsrtop获取的商品id，进行解析
'''
monkey.patch_all()
exe_pool = pool.Pool(80)

redishandler = redis.Redis(host='172.21.15.57', port=6379, db=12)
PROXY_KEY = "pycrawler_proxies:dly"

try:
    url_db = redis.StrictRedis(host='172.21.15.64', port=6379, db=7)
except:
    url_db = None



def download(url, product_data):
    # start_time = time.time()
    #
    # try:
    #     cookies_content = url_db.srandmember('amazon_detail_spider:cookies_set')
    #     if isinstance(cookies_content, bytes):
    #         cookies_content = cookies_content.decode()
    #     cookies_content = json.loads(cookies_content)
    #     time_stamp = str(int(time.time() * 1000))
    #     headers = {"content-type": "application/x-www-form-urlencoded; charset=UTF-8", "pragma": "no-cache",
    #                "sec-fetch-dest": "empty", "sec-fetch-mode": "cors", "sec-fetch-site": "same-origin",
    #                "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36",
    #                "cookies": 'session-id=' + str(cookies_content.get('session_id', '')) + ';ubid-main=' + str(
    #                    cookies_content.get('ubid_main',
    #                                        '')) + ';i18n-prefs=USD;csm-hit=tb:ddddKP9AEMV9PF10XHG4+s-7YR2KP9AEMV9PF10XHG4|' + time_stamp + '&t:' + time_stamp + '&adb:adblk_no;session-token=kRH+cLX+JLmd0T5vC/UW0GmRwwp/KN6OU6E/iWxRzkVnLCzi+24+Ny1QyYKl1GFDCcdc3s2gOQn0+222220xm4aKSipEzNjfUxn12c7xJNIJsyUcWIBITYEhwrKyJaWCgyjQbjMfgVlqtLns3HD8+d/tpVfoo/J6ioZhvKW4DrPtKgCjw92qW0GUzW5ZlGxl;x-wl-uid=15/lJL6ZuCc88bu2UNMVdyUmWE1hS64Bo0NVs4QZXKH2jFMh+0rtV333KutuXXNTQrmD+r3yFfrc='}  # ,"cookies": "session-id=138-8001409-6836868;ubid-main=134-3844772-8227127;i18n-prefs=USD"
    #
    #     payload = {
    #         "url": url,
    #         "headers": headers,
    #     }
    #     web_url = "http://172.21.15.66:8092/asdfa"
    #     web_headers = {
    #         'Content-Type': 'text/plain'
    #     }
    #     datas = json.dumps(payload)
    #     response = requests.request("POST", web_url, headers=web_headers, data=datas)
    #     time.sleep(50)
    #     if response.text is not None:
    #         return response
    #     else:
    #         end_time = time.time()
    #         time_inv = end_time - start_time
    #         if time_inv > 60:
    #             print('超时20分钟还未返回数据，该服务暂停')
    #             sys.exit(0)
    # except Exception as msg:
    #     print('========ID:{0}==========>error:{1}==='.format(product_data, msg))
    #     if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data)):
    #         url_db.sadd('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data))
    #         url_db.lpush("amazon_category_bsrtop:failed_urls_list", json.dumps(product_data))

    resp = None
    success = False
    exe_cnt = 0
    while not success and exe_cnt < 10:
        try:
            exe_cnt += 1
            proxy = redishandler.srandmember(PROXY_KEY)
            if isinstance(proxy, bytes):
                proxy = proxy.decode()
            proxies = {
                "http": "http://databurning:2tQJl*t8@{}".format(proxy),
                "https": "https://databurning:2tQJl*t8@{}".format(proxy)
            }
            print('proxies is ---------', proxies)
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
            cookies = {
                # 'session-id': '143-0582700-9583307',   #144-5953255-9071136
                'session-id': '144-5953255-9071136',   #144-5953255-9071136
                # 'ubid-main': '133-1649099-9448018',     #133-0153621-7443973
                'ubid-main': '133-0153621-7443973',     #133-0153621-7443973
                'i18n-prefs': 'USD',    #i18n-prefs=USD
            }
            resp = requests.get(url, timeout=5, proxies=proxies, cookies=cookies, headers=headers, verify=False)  #, cookies=cookies
            if 'Robot Check' in resp.text:
                print('Robot Check===={}==='.format(exe_cnt))
                success = False
            else:
                success = True
        except:
            if exe_cnt == 10:
                # url_db.sadd(swd_amazon_product_set, url)   #????????????????????
                print('10次都出现Robot Check======={}=========='.format(url))
                # url_db.lpush("amazon_normal:failed_category_url", url)
    if success:
        return resp
    else:
        print('10次抓取都失败====={}=========='.format(url))
        if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data)):
            url_db.sadd('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data))
            url_db.lpush("amazon_category_bsrtop:failed_urls_list", json.dumps(product_data))


def clear_special_xp(data, xp):
    data = copy.copy(data)
    result = data.xpath(xp)
    for i in result:
        try:
            i.getparent().remove(i)
        except Exception as e:
            print(e)
    return data


def parse_list(url, product_data):
    content_dict = dict()

    resp = download(url, product_data)
    # productID = re.findall(r'/(\w{10})', url)
    # pid = productID[0] if productID else None  # 商品唯一标识
    pid = product_data.get('pid', '')
    if not pid:
        print('没有找到商品ID')
    print('--{}---开始抓取商品详情----{}---'.format(time.strftime('%Y-%m-%d %H:%M:%S'), pid))
    # with open('{}.html'.format(str(os.getpid())), 'a+', encoding='utf-8') as ee:
    #    ee.write(resp.text.replace('\n', '') + '\n')

    url = 'https://www.amazon.com/dp/{}/'.format(pid)  # 商品链接
    source = 'amazon'  # 网站来源

    try:
        content = etree.HTML(resp.text)
        content = clear_special_xp(content, '//style|//script')  # 去除杂质
    except:
        if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data)):
            url_db.sadd('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data))
            url_db.lpush("amazon_category_bsrtop:failed_urls_list", json.dumps(product_data))
        return

    if 'MEOW' not in resp.text:
        print('*****MEOW不在源码里******')
        url_db.lpush("amazon_category_bsrtop:403_list", json.dumps(product_data))

    country = content.xpath('''(//div[@id="glow-ingress-block"]//span)[2]/text()''')[0]
    country = country.replace('\n', '').replace(' ', '')
    print('====This is {}=========='.format(country))
    # if 'NewYork' not in country:
    #     print('-----------地址发生了变化--------------')
    # if not url_db.sismember('amazon_detail_spider:failed_urls_set', pid):
    #     url_db.sadd('amazon_detail_spider:failed_urls_set', pid)
    #     url_db.lpush("amazon_detail_spider:failed_urls_list", pid)

    category_list = content.xpath(
        '''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]/text()''')
    category = [x.replace('\n', '').replace(' ', '').strip() for x in category_list]  # 导航列表
    new_category = ">".join(category)  # ca

    category_id_list = []  # 导航列表的值
    breadcrumb_url_list = content.xpath(
        '''//ul[@class="a-unordered-list a-horizontal a-size-small"]//span//a[contains(@class,"a-link")]//@href''')  # .getall()
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
    # 标题
    title_content = content.xpath('''//h1//span[@id="productTitle"]/text()''')[0]
    title_content1 = title_content.replace('\n', '').replace('Amazon.com: ', '').replace('Amazon.com : ', '')
    try:
        title = title_content1.split(':')[0].strip()
    except:
        title = title_content1.strip()

    title_content = content.xpath('''//title/text()''')[0]
    title_content1 = title_content.replace('\n', '').replace('Amazon.com: ', '').replace('Amazon.com : ', '')
    try:
        title_flag = title_content1.split(':')[0].strip()
    except:
        title_flag = title_content1.strip()

    if 'Robot Check' in title_flag:
        print('======Robot Check出现了=={}================'.format(pid))


    # 价格
    try:
        if 'Currently unavailable' in resp.text or 'Available from' in resp.text:
            price = ''  # 无货
            sale_status = 2
        else:
            price = content.xpath('''//div[@id="buyNew_noncbb"]//span/text()|//div[@id="cerberus-data-metrics"]//@data-asin-price|//div[@id="price"]//span[@id="priceblock_ourprice"]/text()|//span[@id="price_inside_buybox"]/text()''')[0]
            sale_status = 1
    except:
        print('@@@@@@价格有问题{}@@@@@@@@@@@@@@@'.format(pid))
        price = '-1'
        sale_status = 0
    price = price.replace('\n', '').replace(' ', '')
    if price == '-1' or not price:
        price = price
    else:
        if '$' not in price:
            price = '$' + price
    price = price.replace('$', '').strip()   #替换掉价格标签符号

    brand_name = content.xpath('''//a[@id="bylineInfo"]/text()''')[0]
    brand_name = brand_name.replace('brand_name', '').strip()
    # 图片
    images_content = content.xpath('''//div[@id="altImages"]//ul//li//img//@src''')  # .getall()
    images = [x.strip() for x in images_content]

    crawler_tm = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))  # 采集时间


    shop_url = content.xpath('''//a[@id="bylineInfo"]/@href''')[0]
    if shop_url:
        if 'http' not in shop_url:
            shop_url = 'https://www.amazon.com' + shop_url
        else:
            shop_url = ''

    # 商品评分/好评率---评分内容获取前面的数字|评论数替换成数字
    if 'acrPopover' in resp.text:
        star_score_content = content.xpath('''(//span[@id="acrPopover"])[1]//@title''')[0]
        if star_score_content:
            if 'out' in star_score_content:
                score = star_score_content.split('out')[0].strip()
            else:
                score = ''
                print('------score_xpath错误---{}---------')
        comments_num_content = content.xpath('''(//a[@id="acrCustomerReviewLink"]//span[@id="acrCustomerReviewText"])[1]/text()''')[0]
        if comments_num_content:
            comment_count = comments_num_content.replace('ratings', '').replace(',', '').strip()
    else:
        print('======={}没有评论==============='.format(pid))
        comment_count = 0
        score = ''

    #评论中各个星级对应的比例
    star_dict = dict()
    star_level = content.xpath('''//table[@id="histogramTable"]//tr//td[1]//a/text()''')
    star_proportion = content.xpath('''//table[@id="histogramTable"]//tr//td[3]//a/text()''')
    for x, y in zip(star_level, star_proportion):
        x = x.strip()
        y = y.strip()
        star_dict[x] = y

    #################解析bsr部分#################
    summary_content = dict()
    summary_key_list_ = content.xpath('''//table[@id="productDetails_techSpec_section_1"]//tr''')  # .getall()
    for item in summary_key_list_:
        key = item.xpath('''./th/text()''')
        value = item.xpath('''./td//text()''')
        zz_list = list()
        xx = ''
        for value_temp in value:
            xx += value_temp.replace('\n', '')
        zz_list.append(xx)
        for k, v in zip(key, zz_list):
            k = k.replace('\n', '').replace(' ', '')
            summary_content[k] = v

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

    # 添加bsr    B00WEYVE5U|B00WEYVE5U
    other_style_list = content.xpath('''//li[@id="SalesRank"]''')
    for item in other_style_list:
        style_key = item.xpath('''./b/text()''')[0]
        style_key = style_key.replace('Amazon', '').replace(' ', '').replace(':', '')
        style_value = item.xpath('''./text()|./a/text()|.//span/a/text()|.//span/text()''')
        style_value1 = ''
        for i in style_value:
            style_value1 += i.strip()
        summary_content[style_key] = style_value1

    # -------添加其他参数------------
    other_dict = dict()
    other_style_list1 = content.xpath('''//div[@id="descriptionAndDetails"]//div[@id="detailBullets_feature_div"]//ul//li''')
    for item1 in other_style_list1:
        item_key_list = item1.xpath('''.//span[@class="a-list-item"]/span[@class="a-text-bold"]/text()''')
        item_value_list = item1.xpath('''(.//span[@class="a-list-item"]/span)[2]/text()''')
        for item_key, item_value in zip(item_key_list, item_value_list):
            if not item_key:
                continue
            else:
                other_dict[item_key] = item_value

    other_style_list2 = content.xpath('''//div[@class="pdTab"]//tr[@id="SalesRank"]''')
    for item1 in other_style_list2:
        item_key_list = item1.xpath('''./td[@class="label"]//text()''')
        item_value_list = item1.xpath('''./td[@class="value"]//text()''')
        zz = list()
        xx = ''
        for value_temp in item_value_list:
            xx += value_temp.replace('\n', '')
        zz.append(xx)
        for k, v in zip(item_key_list, zz):
            k = k.replace('\n', '').replace(' ', '').replace('Amazon', '').replace(':', '')
            sellers_rank[k] = v

    summary_content.update(other_dict)
    summary_content.update(sellers_rank)

    # add--->新bsr(B000XEV9YE|B004TRUDSO|B084VLHXWH)
    # other_bsr = dict()
    # xx = ''
    # other_bsr_parse = content.xpath('''//ul[contains(@class,"detail-bullet-list")]//a[contains(@href,'bestsellers')]''')
    # for other_bsr_item in other_bsr_parse:
    #     value = other_bsr_item.xpath('''./../text()''')[0] + other_bsr_item.xpath('''./text()''')[0]
    #     if value:
    #         xx += value
    # if xx:
    #     other_bsr['BestSellersRank'] = xx
    #     summary_content.update(other_bsr)

    other_bsr = dict()
    xx = ''
    other_bsr_parse = content.xpath('''//ul[contains(@class,"detail-bullet-list")]//span[contains(@class,"a-list-item")]/text()|//ul[contains(@class,"detail-bullet-list")]//a[contains(@href,'bestsellers')]/text()''')
    for other_bsr_item in other_bsr_parse:
        xx += other_bsr_item.replace('\n', '')
    if xx:
        other_bsr['BestSellersRank'] = xx
        summary_content.update(other_bsr)

    other_bsr1 = dict()
    xx = ''
    other_bsr_parse = content.xpath('''//li[@id="SalesRank"]/text()|//li[@id="SalesRank"]/a/text()|//ul[@class="zg_hrsr"]//span/text()|//ul[@class="zg_hrsr"]//span/a/text()''')
    for other_bsr_item in other_bsr_parse:
        xx += other_bsr_item.replace('\n', '')
    if xx:
        other_bsr1['BestSellersRank'] = xx
        summary_content.update(other_bsr1)


    if 'Sellers Rank' in resp.text or 'sellers rank' in resp.text:
        if 'BestSellersRank' in summary_content.keys():
            bsr = summary_content.get('BestSellersRank', '')
        else:
            bsr = '-1'
            print('BestSellersRank没抓取到----{}'.format(pid))
    else:
        bsr = ''
        print('----{}----没有BestSellersRank'.format(pid))
        if not url_db.sismember('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data)):
            url_db.sadd('amazon_category_bsrtop:failed_urls_set', json.dumps(product_data))
            url_db.lpush("amazon_category_bsrtop:failed_urls_list", json.dumps(product_data))
        return None
    print('%%%%%%%%%%%%%%%%{}%%%%%%%%%%%%%%%%%%%'.format(bsr))

    # 2020_07_27--swd_add_marketplaceID--
    marketplace_content = dict()
    try:
        me = content.xpath('''//input[@id="merchantID"]//@value|//input[@id="usedMerchantID"]//@value''')[0]
        if me:
            me = me
            marketplaceID = re.search(r'marketplaceId\s*[\'\"]\s*[:：]\s*[\'\"]\s*(.*?)\s*[\'\"]\s*', resp.text).group(1)
            marketplace_content['me'] = me
            marketplace_content['marketplaceID'] = marketplaceID
    except:
        me = ''
        marketplaceID = ''
        print('----该商品没有Sold by榜单-------')
        marketplace_content['me'] = me
        marketplace_content['marketplaceID'] = marketplaceID

    # except Exception as mess:
    #     print('详情解析错误：{}'.format(mess))
    # url_db.lpush("amazon_detail_spider:failed_urls", pid)

    shop_id = marketplace_content  # 店铺id
    shop_starts = ''  # 开店时间
    shop_name = ''  # 店铺名字
    shop_evaluates = ''  # 店铺评分
    shop_credi_level = ''  # 店铺等级
    ori_price = ''  # 原价
    descibe = ''  # 商品详细描述
    descibe_more = ''  # 商品更多信息
    sku_list = ''  # sku商品列表
    brand_id = ''  # 品牌id
    batch_tm = product_data.get('batch_time', '')  # 批次时间  #####
    # 未找到的字段---添加商品列表解析
    sku_list = []  # sku商品列表
    sku_id = ''
    try:
        spu_id = re.search('parentAsin\s*[\"\']\s*[:：]\s*[\"\']\s*(\w{10})\s*[\"\']\s*', resp.text).group(1)
        if spu_id:
            sku_id_content = re.search('dimensionToAsinMap\s*[\"\']\s*[:：]\s*(.*?})\s*,', resp.text).group(1)
            sku_id_dict = json.loads(sku_id_content)
            for sku_id in sku_id_dict.values():
                sku_list.append(sku_id)
    except:
        spu_id = pid
        sku_list = []
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

    content_dict['pid'] = pid
    content_dict['sku_id'] = sku_id
    content_dict['spu_id'] = spu_id
    content_dict['url'] = url
    content_dict['sale_status'] = sale_status
    content_dict['source'] = source
    content_dict['category'] = new_category
    content_dict['title'] = title
    content_dict['brand_id'] = brand_id
    content_dict['brand_name'] = brand_name
    content_dict['model'] = summary_content  ##############
    content_dict['price'] = price
    content_dict['ori_price'] = ori_price
    content_dict['support'] = support
    content_dict['shop_id'] = shop_id
    content_dict['shop_starts'] = shop_starts
    content_dict['shop_name'] = shop_name
    content_dict['shop_evaluates'] = shop_evaluates
    content_dict['shop_credi_level'] = shop_credi_level
    content_dict['score'] = score
    content_dict['descibe'] = descibe
    content_dict['descibe_more'] = descibe_more
    content_dict['sku_list'] = sku_list
    content_dict['sales_count'] = sales_count
    content_dict['sales_count_month'] = sales_count_month
    content_dict['comment_count'] = comment_count
    content_dict['praise_count'] = praise_count
    content_dict['medium_count'] = star_dict  #####################
    content_dict['bad_count'] = bad_count
    content_dict['storage_count'] = storage_count
    content_dict['collection_count'] = collection_count
    content_dict['delivery_from'] = delivery_from
    content_dict['batch_tm'] = batch_tm
    content_dict['crawler_tm'] = crawler_tm
    content_dict['presell_count'] = presell_count
    content_dict['presell_price'] = presell_price
    content_dict['goods_types'] = goods_types
    content_dict['promo_list'] = promo_list
    content_dict['images'] = images
    content_dict['subtitle'] = subtitle
    content_dict['bsr'] = bsr
    content_dict.update(category_tree)
    # print(content_dict)
    url_db.lpush('amazon_category_bsrtop:detail_successful_list', json.dumps(product_data))
    #
    with open('/mnt/data/weidong.shi/file/amazon/product_info/bsrtop_product_info_' + time.strftime(
            '%Y-%m-%d') + '_' + str(os.getpid()) + '.txt', 'a+', encoding='utf-8') as ff:
        # with open(time.strftime('%Y-%m-%d') + '_' + str(os.getpid()) + '.txt', 'a+', encoding='utf-8') as ff:
        ff.write(json.dumps(content_dict) + '\n')


def get_data():
    job = []
    print('start_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))
    while 1:
        redis_dict = url_db.lpop('amazon_category_bsrtop:produce_id_list')  #
        if redis_dict:
            if isinstance(redis_dict, bytes):
                product_data = redis_dict.decode()
                product_data = json.loads(product_data)
                product_id = product_data.get('pid', '')
                product_url = 'https://www.amazon.com/dp/{}'.format(product_id)
                job.append(exe_pool.spawn(parse_list, product_url, product_data))
        else:
            print('队列已消耗完毕，退出')
            break
    gevent.joinall(job)
    print('END_time:{}'.format(time.strftime('%Y-%m-%d %H:%M:%S')))


if __name__ == '__main__':
    get_data()


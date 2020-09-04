# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.downloadermiddlewares.httpcompression import HttpCompressionMiddleware
import time
import redis
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from twisted.web._newclient import ResponseNeverReceived


class AmazonUsSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


# class AmazonUsDownloaderMiddleware:
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         # This method is used by Scrapy to create your spiders.
#         s = cls()
#         crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
#         return s
#
#     def process_request(self, request, spider):
#         # Called for each request that goes through the downloader
#         # middleware.
#
#         # Must either:
#         # - return None: continue processing this request
#         # - or return a Response object
#         # - or return a Request object
#         # - or raise IgnoreRequest: process_exception() methods of
#         #   installed downloader middleware will be called
#         return None
#
#     def process_response(self, request, response, spider):
#         # Called with the response returned from the downloader.
#
#         # Must either;
#         # - return a Response object
#         # - return a Request object
#         # - or raise IgnoreRequest
#         return response
#
#     def process_exception(self, request, exception, spider):
#         # Called when a download handler or a process_request()
#         # (from other downloader middleware) raises an exception.
#
#         # Must either:
#         # - return None: continue processing this exception
#         # - return a Response object: stops process_exception() chain
#         # - return a Request object: stops process_exception() chain
#         pass
#
#     def spider_opened(self, spider):
#         spider.logger.info('Spider opened: %s' % spider.name)
PROXY_KEY = "weifan_ip_swd"



class RedisProxyMiddleware(HttpProxyMiddleware):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    redisclient = redis.StrictRedis(host='172.21.15.57', port=6379, db=12)

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
        # 120.12.188.96: 57114

        try:
            proxy_content = self.redisclient.srandmember("pycrawler_proxies:dly")
            if isinstance(proxy_content, bytes):
                proxy_content = proxy_content.decode()
            proxy = "http://databurning:2tQJl*t8@{}".format(proxy_content.strip())
            spider.logger.info(proxy)
            print('=======代理是===={}============'.format(proxy))
            #redishandler.rpush(PROXY_KEY,proxy_content)
            request.meta["proxy"] = proxy
            # request.headers = request.headers.to_string()

            # return request
            # return request
        except Exception as ee:
            spider.logger.error("获取代理失败，{}，1秒后重试。".format(ee))


    def process_exception(self, request, exception, spider):
        """
        处理由于使用代理导致的连接异常 则重新换个代理继续请求
        """
        if isinstance(exception, self.DONT_RETRY_ERRORS):
            while 1:
                try:
                    proxy_content = self.redisclient.srandmember("pycrawler_proxies:dly")
                    if isinstance(proxy_content, bytes):
                        proxy_content = proxy_content.decode()

                    proxy = "http://databurning:2tQJl*t8@{}".format(proxy_content.replace('%20', '').replace(' ', '').strip())
                    spider.logger.info('重试代理{}'.format(proxy))
                    print(proxy,'----第二次加代理---------')
                    #redishandler.rpush(PROXY_KEY,proxy_content)
                    request.meta["proxy"] = proxy
                    break
                    # return request
                except Exception as ee:
                    spider.logger.error("获取代理失败，{}，1.1秒后重试。".format(ee))
                    break

from scrapy.downloadermiddlewares.useragent import UserAgentMiddleware
import random

class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    # the default user_agent_list composes chrome,I E,firefox,Mozilla,opera,netscape
    # for more user agent strings,you can find it in http://www.useragentstring.com/pages/useragentstring.php
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]

    def process_request(self, request, spider):
        ua = random.choice(self.user_agent_list)
        if ua:
            request.headers.setdefault('User-Agent', ua)

import requests
from scrapy.http import HtmlResponse as Response

# class DownloaderMiddleware(object):
#     # Not all methods need to be defined. If a method is not defined,
#     # scrapy acts as if the downloader middleware does not modify the
#     # passed objects.
#
#     def process_request(self, request, spider):
#         url=request.url
#         s=requests.Session()
#         print(request.meta["proxy"])
#         proxies = {
#             "http": request.meta["proxy"].replace("https", "http"),
#             "https": request.meta["proxy"]
#         }
#         r = s.get(url, headers=spider.headers, proxies=proxies)
#         r.encoding='utf-8'
#         response=Response(url=r.url,status=r.status_code, body=r.content,
#                           encoding=request.encoding, request=request)
#         # time.sleep(5)
#         return response


import requests
from scrapy.http import HtmlResponse as Response
from scrapy import signals
from twisted.internet import defer, reactor
import time


class DownloaderMiddleware(object):
    redisclient = redis.StrictRedis(host='172.21.15.57', port=6379, db=12)
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @defer.inlineCallbacks
    def process_request(self, request, spider):
        container=[]
        out = defer.Deferred()
        reactor.callInThread(self._get_res, request, container, out, spider)
        yield out
        if len(container) > 0:
            defer.returnValue(container[0])

    def _get_res(self, request, container, out, spider):
        # try:
        #     url = request.url
        #     proxies = {
        #         "http": request.meta["proxy"],
        #         "https": request.meta["proxy"].replace("https", "http"),
        #     }
        #     headers = request.headers.to_unicode_dict()
        #
        #     while 1:
        #         try:
        #             r = requests.get(url, headers=headers, proxies=proxies, timeout=5)
        #             break
        #         except:
        #             continue
        #     r.encoding = request.encoding
        #     response = Response(url=r.url, status=r.status_code, body=r.content,
        #                       encoding=request.encoding, request=request)
        #     container.append(response)
        #     reactor.callFromThread(out.callback, response)
        #
        # except Exception as e:
        #     err=str(type(e))+' '+str(e)
        #     reactor.callFromThread(out.errback, ValueError(err))

        try:
            url = request.url
            # proxies = {
            #     "http": request.meta["proxy"],
            #     "https": request.meta["proxy"].replace("https", "http"),
            # }
            headers = request.headers.to_unicode_dict()

            while 1:
                proxy_content = self.redisclient.srandmember("pycrawler_proxies:dly")
                if isinstance(proxy_content, bytes):
                    proxy_content = proxy_content.decode()
                proxy = {
                    "http": "http://{}".format(proxy_content),
                    "https": "https://{}".format(proxy_content)
                }
                #spider.logger.info(proxy)
               # print('=======代理是===={}============'.format(proxy))
                cookies = {
                    # "skin": "noskin",
                    # "lc-main": "en_US",
                    # "i18n-prefs": "USD",
                    # 'session-id': '143-0582700-9583307',   #144-5953255-9071136
                    'session-id': '144-5953255-9071136',  # 144-5953255-9071136
                    # 'ubid-main': '133-1649099-9448018',     #133-0153621-7443973
                    'ubid-main': '133-0153621-7443973',  # 133-0153621-7443973
                    'i18n-prefs': 'USD',  # i18n-prefs=USD
                }
                try:
                    r = requests.get(url, headers=headers, proxies=proxy, timeout=5,cookies=cookies)
                    x = r.headers
                    y = r.cookies
                    #print(x ,'====@@@@@@@@@@@=======', y)
                    break
                except:

                    continue
            r.encoding = request.encoding
            response = Response(url=r.url, status=r.status_code, body=r.content,
                              encoding=request.encoding, request=request)
            container.append(response)
            reactor.callFromThread(out.callback, response)

        except Exception as e:
            err=str(type(e))+' '+str(e)
            reactor.callFromThread(out.errback, ValueError(err))


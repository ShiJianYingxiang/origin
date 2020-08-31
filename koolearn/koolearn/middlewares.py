# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
import time
import redis
from scrapy.downloadermiddlewares.httpproxy import HttpProxyMiddleware
from twisted.internet.error import TimeoutError, ConnectionRefusedError, ConnectError
from twisted.web._newclient import ResponseNeverReceived


class KoolearnSpiderMiddleware:
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


class RedisProxyMiddleware(HttpProxyMiddleware):
    DONT_RETRY_ERRORS = (TimeoutError, ConnectionRefusedError, ResponseNeverReceived, ConnectError, ValueError)
    redisclient = redis.StrictRedis(host='172.21.15.57', port=6379, db=12)

    def process_request(self, request, spider):
        """
        将request设置为使用代理
        """
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
                    print(proxy, '----第二次加代理---------')
                    #redishandler.rpush(PROXY_KEY,proxy_content)
                    request.meta["proxy"] = proxy
                    break
                    # return request
                except Exception as ee:
                    spider.logger.error("获取代理失败，{}，1.1秒后重试。".format(ee))
                    break






































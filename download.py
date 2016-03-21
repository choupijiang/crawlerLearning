# -*- coding: utf-8 -*-

import urlparse
import urllib2
import random
import socket
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from throttle import Throttle


class Downloader(object):
    def __init__(self, delay=5, user_agent='wswp', proxies=None, num_retries=1, cache=None, opener=None, timeout=30):
        socket.setdefaulttimeout(timeout)
        self.throttle = Throttle(delay)
        self.user_agent = user_agent
        self.proxies = proxies
        self.num_retries = num_retries
        self.cache = cache
        self.opener = opener

    def __call__(self, url):
        result = None
        if self.cache:
            try:
                result = self.cache[url]
            except KeyError:
                pass
            else:
                if self.num_retries > 0 and 500 <= result['code'] < 600:
                    result = None
        if result is None:
            self.throttle.wait(url)
            proxy = random.choice(self.proxies) if self.proxies else None
            headers = {'User-agent': self.user_agent}
            result = self.download(url, headers, proxy, num_retries=self.num_retries)
            if self.cache:
                self.cache[url] = result
        return result['html']

    def download(self, url, headers,proxy=None, num_retries=2, data=None):
        print 'downloading:', url
        request = urllib2.Request(url, data, headers or {})
        opener = self.opener or urllib2.build_opener()
        if proxy:
            proxy_params = {urlparse.urlparse(url).scheme: proxy}
            opener.add_handler(urllib2.ProxyHandler(proxy_params))
        try:
            response = opener.open(request)
            html = response.read()
            code = response.code
        except urllib2.URLError as e:
            print 'Download Error:', e.reason
            html = ''
            if hasattr(e, 'code'):
                code = e.code
                if 500 <= e.code < 600 and num_retries > 0:
                    self.download(url, headers, num_retries-1, data)
            else:
                code = None
        return {'html': html, 'code': code}
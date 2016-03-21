# -*- coding: utf-8 -*-

import re
import urlparse
import datetime
import os
import pickle
import zlib
import shutil
import sys

reload(sys)
sys.setdefaultencoding('utf8')



class DiskCache(object):
    def __init__(self, cache_dir='cache',  compress=False, expires=datetime.timedelta(days=30)):
        self.cache_dir = cache_dir
        self.compress = compress
        self.expires = expires

    def url_to_path(self, url):
        """
        Create file system path for this URL
        :param url:
        :return:
        """
        components = urlparse.urlsplit(url)
        path = components.path
        if not path:
            path = '/index.html'
        elif path.endswith('/'):
            path += 'index.html'
        filename = components.netloc + path + components.query
        filename = re.sub('[^/0-9a-zA-Z\-.,;_ ]', '_', filename)
        filename = '/'.join(segment[:250] for segment in filename.split('/'))
        return os.path.join(self.cache_dir, filename)

    def __getitem__(self, url):
        """
        Load data from disk for this URL
        :param url:
        :return:
        """
        path = self.url_to_path(url)
        if os.path.exists(path):
            with open(path, 'rb') as fp:
                data = fp.read()
                if self.compress:
                    data = zlib.decompress(data)
                result, timestamp = pickle.loads(data)
                if self.has_expired(timestamp):
                    raise KeyError(url + ' has expired')
                return  result
        else:
            raise KeyError(url + ' dose not exist')

    def __setitem__(self, url, result):
        """
        Save data to disk for this url
        :param url:
        :param result:
        :return:
        """
        path = self.url_to_path(url)
        folder = os.path.dirname(path)
        if not os.path.exists(folder):
            os.makedirs(folder)
        data = pickle.dumps((result, datetime.datetime.utcnow()))
        if self.compress:
            data = zlib.compress(data)
        with open(path, 'wb') as fp:
            fp.write(data)

    def has_expired(self, timestamp):
        """
        Return whether this timestamp has expired
        :param timestamp:
        :return:
        """
        return datetime.datetime.utcnow() - timestamp > self.expires


    def clear(self):
        if os.path.exists(self.cache_dir):
            shutil.rmtree(self.cache_dir)
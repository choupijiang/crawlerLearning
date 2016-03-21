# -*- coding: utf-8 -*-
try:
    import cPickle as pickle
except ImportError:
    import pickle

import datetime
import zlib
import sys
import elasticsearch

reload(sys)
sys.setdefaultencoding('utf8')

class ElasticCache(object):
    """
    Wrapper around EsDb to cache downloads
    """
    def __init__(self, client=None, index=None, doc_type=None, expires=datetime.timedelta(days=30)):
        """
        client: es database client
        expires: timedelta of amount of time before a cache entry is considered expired
        """
        self.es = elasticsearch.Elasticsearch(client)
        self.index = index
        self.doc_type = doc_type

    def __getitem__(self, url):
        """
        Load value at this URL
        :param item:
        :return:
        """
        try:
            record = self.es.get(index=self.index, doc_type=self.doc_type, id=url)['_source']['result']
            return record
        except elasticsearch.NotFoundError as e:
            raise KeyError(url + ' does not exist')

    def __setitem__(self, url, reslut):
        """
        save the content of the url
        :param url:
        :param reslut:
        :return:
        """
        record = {'result': reslut, 'timestamp': datetime.datetime.utcnow()}
        try:
            self.es.index(index=self.index, doc_type=self.doc_type, id=url, body=record)
        except Exception as e:
            print e
            print url, 'failed'
    def clear(self):
        self.es.indices.delete(index=self.index)
# -*- coding: utf-8 -*-

import sys
import re
import urlparse
import urllib2
import threading
import datetime
import time
import Queue
import robotparser
from crawler import link_crawler, threaded_crawler
from download import Downloader
from disk_cache import DiskCache
from elastic_cache import ElasticCache

from bs4 import BeautifulSoup
import lxml.html
import csv
reload(sys)
sys.setdefaultencoding('utf8')



try:
    from PySide.QtGui import *
    from PySide.QtCore import *
    from PySide.QtWebKit import *
except ImportError:
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from PyQt4.QtWebKit import *


FIELDS = ('area', 'population', 'iso', 'country', 'capital',
          'continent', 'tld', 'currency_code', 'currency_name', 'phone',
          'postal_code_format', 'postal_code_regex', 'languages',
          'neighbours')

def regex_scraper(html):
    results = {}
    for field in FIELDS:
        results[field] = re.search('<tr id="places_%s__row">.*?<td class="w2p_fw">(.*?)</td>' % field, html).groups()[0]
        return results

def beautiful_soup_scraper(html):
    soup = BeautifulSoup(html, 'html.parser')
    results = {}
    for field in FIELDS:
        results[field] = soup.find('table').find('tr', id='places_{}__row'.format(field)).find('td', class_='w2p_fw').text
    return results


def lxml_scraper(html):
    tree = lxml.html.fromstring(html)
    results = {}
    for field in FIELDS:
        results[field] = tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content()
    return results


def scrape_callback(url, html):
    if re.search('/view/', url):
        tree = lxml.html.fromstring(html)
        row = [tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content() for field in FIELDS]
        print url, row

class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            self.writer.writerow(row)

def webkit_download(url):
    app = QApplication([])
    webview = QWebView()
    webview.loadFinished.connect(app.quit)
    webview.load(url)
    app.exec_() # delay here until download finished
    return webview.page().mainFrame().toHtml()


def webkit_search(url):
    app = QApplication([])
    webview = QWebView()
    webview.loadFinished.connect(app.quit)
    webview.load(QUrl(url))
    app.exec_()

    webview.show()
    frame = webview.page().mainFrame()
    frame.findFirstElement('#search_term').setAttribute('value', '.')
    frame.findFirstElement('#page_size option:checked').setPlainText('1000')
    frame.findFirstElement('#search').evaluateJavaScript('this.click()')

    elements = None
    while not elements:
        app.processEvents()
        elements = frame.findAllElements('#results a')
    countries = [e.toPlainText().strip() for e in elements]
    print countries

if __name__ == "__main__":

    #Section 1
    # url = 'http://example.webscraping.com/view/Andorra-6'
    # html = download(url, headers={'User-agent': 'GoodCrawler'})
    # print re.findall('<td class="w2p_fw">(.*?)</td>', html)[1]
    #
    # from bs4 import BeautifulSoup
    # soup = BeautifulSoup(html, "lxml")
    # tr = soup.find(attrs={'id':'places_area__row'})
    # td = tr.find(attrs={'class': 'w2p_fw'})
    # area = td.text
    # print area
    #
    # import lxml.html
    # tree = lxml.html.fromstring(html)
    # td = tree.cssselect('tr#places_area__row > td.w2p_fw')[0]
    # area = td.text_content()
    # print area


    #Section 2
    # times = {}
    # html = urllib2.urlopen('http://example.webscraping.com/view/United-Kingdom-239').read()
    # NUM_ITERATIONS = 1000 # number of times to test each scraper
    # for name, scraper in ('Regular expressions', regex_scraper), ('Beautiful Soup', beautiful_soup_scraper), ('Lxml', lxml_scraper):
    #     times[name] = []
    #     # record start time of scrape
    #     start = time.time()
    #     for i in range(NUM_ITERATIONS):
    #         if scraper == regex_scraper:
    #             # the regular expression module will cache results
    #             # so need to purge this cache for meaningful timings
    #             re.purge()
    #         result = scraper(html)
    #
    #         # check scraped result is as expected
    #         assert(result['area'] == '244,820 square kilometres')
    #         times[name].append(time.time() - start)
    #     # record end time of scrape and output the total
    #     end = time.time()
    #     print '{}: {:.2f} seconds'.format(name, end - start)
    #
    # writer = csv.writer(open('times.csv', 'w'))
    # header = sorted(times.keys())
    # writer.writerow(header)
    # print times
    # for row in zip(*[times[scraper] for scraper in header]):
    #     writer.writerow(row)

    #Section 3
    # link_crawler('http://example.webscraping.com/index/1', '/(index|view)', scrape_callback=scrape_callback ,delay=0, num_retries=1, max_depth=1, user_agent='GoodCrawler')
    # link_crawler('http://example.webscraping.com/', '/(index|view)', scrape_callback=ScrapeCallback(), delay=0, num_retries=1, max_depth=3, max_urls=40, user_agent='GoodCrawler')

    #Section 4
    # import csv
    # from zipfile import ZipFile
    # from StringIO import StringIO
    # from crawler import Downloader
    # #
    # # D = Downloader()
    # # zipped_data = D('http://s3.amazonaws.com/alexa-static/top-1m.csv.zip')
    # # urls = []
    # # with ZipFile(StringIO(zipped_data)) as zf:
    # #     csv_filename = zf.namelist()[0]
    # #     for _, website in csv.reader(zf.open(csv_filename)):
    # #         urls.append('http://' + website)
    #
    # class AlexaCallback(object):
    #     def __init__(self, max_urls=50):
    #         self.max_urls = max_urls
    #         self.seed_url = 'http://www.baidu.com'
    #
    #     def __call__(self, url, html):
    #         if url == self.seed_url:
    #             urls = []
    #             csv_filename = "top-1m.csv"
    #             for _, website in csv.reader(open(csv_filename)):
    #                 urls.append('http://' + website)
    #                 if len(urls) == self.max_urls:
    #                     break
    #             return urls
    #
    # scrape_callback = AlexaCallback()
    # import time
    #
    # # print "suquential crawler"
    # # start = time.time()
    # # # for url in scrape_callback():
    # # link_crawler(seed_url=scrape_callback.seed_url,
    # #              cache=DiskCache(),
    # #              scrape_callback=scrape_callback,
    # #              user_agent='GoodCrawler',
    # #              num_retries= 1
    # #          )
    # # end = time.time()
    # # print "* Elapsed time: %3.2f seconds" % (end - start)
    # # * Elapsed time: 44.92 seconds
    # print "threading crawler"
    # start = time.time()
    # threaded_crawler(scrape_callback.seed_url, scrape_callback=scrape_callback, cache=ElasticCache('10.208.63.12:8200', index='crawler', doc_type='test'), max_threads=20, timeout=10)
    # end = time.time()
    # print "* Elapsed time: %3.2f seconds" % (end - start)
    # #  * Elapsed time: 20.01 seconds

    #section 5
    # url = 'http://example.webscraping.com/dynamic'
    # D = Downloader(cache=ElasticCache('10.208.63.12:8200', index='crawler', doc_type='test'), delay=10, user_agent='GoodCrawler', proxies=None, num_retries=2, timeout=30)
    # html = D(url)
    # tree = lxml.html.fromstring(html)
    # print 'result:', tree.cssselect('#result')[0].text_content()
    #
    # html = webkit_download(url)
    # tree = lxml.html.fromstring(html)
    # print tree.cssselect('#result')[0].text_content()

    # url = 'http://example.webscraping.com/search'
    # html = webkit_search(url)

    from selenium import webdriver
    driver = webdriver.Firefox()
    driver.get('http://example.webscraping.com/search')
    driver.find_element_by_id('search_term').send_keys('.')
    js = "document.getElementById('page_size').options[1].text = '1000'"
    driver.execute_script(js)
    driver.find_element_by_id('search').click()
    driver.implicitly_wait(30)
    links = driver.find_elements_by_css_selector('#results a')
    countries = [link.text for link in links]
    print countries
    driver.close()


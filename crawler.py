# -*- coding: utf-8 -*-


import re
import urlparse
import time
import Queue
import robotparser
import threading
import sys
reload(sys)
sys.setdefaultencoding('utf8')
from download import Downloader
from throttle import Throttle
from disk_cache import DiskCache

def get_links(html):
    """Return a list of links from html
    """
    webpage_regex = re.compile('<a[^>]+href=["\'](.*?)["\']', re.IGNORECASE)
    return webpage_regex.findall(html)

def get_robots(url):
    """
    Initialize robots parser for this domain.
    :param url:
    :return:
    """
    rp = robotparser.RobotFileParser()
    rp.set_url(urlparse.urljoin(url, '/robots.txt'))
    rp.read()
    return rp

def normalize(seed_url, link):
    """Normalize this URL by removing hash and adding domain
    """
    link, _ = urlparse.urldefrag(link)
    return  urlparse.urljoin(seed_url, link)

def same_domain(url1, url2):
    """Return True if both URL's belong to same domain
    """
    return urlparse.urlparse(url1).netloc == urlparse.urlparse(url2).netloc


def link_crawler(seed_url, link_regex=None, delay=5, max_depth=-1, max_urls=-1, headers=None,
                 user_agent='wswp', proxies=None, num_retries=1, scrape_callback=None, cache=None):
    crawl_queue = Queue.deque([seed_url])
    seen = {seed_url: 0}
    num_urls = 0
    # rp = get_robots(seed_url)
    D = Downloader(delay=delay, user_agent=user_agent, proxies=proxies,
                            num_retries=num_retries, cache=cache)
    thrtl = throttle.Throttle(delay)
    headers = headers or {}
    if user_agent:
        headers['User-agent'] = user_agent

    while crawl_queue:
        url = crawl_queue.pop()
        if True : # rp.can_fetch(user_agent, url):
            print url
            thrtl.wait(url)
            html = D(url)
            links = []
            if scrape_callback:
                links.extend(scrape_callback(url, html) or [])
            depth = seen[url]
            if depth != max_depth:
                if link_regex:
                    links.extend(link for link in get_links(html) if re.match(link_regex, link))
                for link in links:
                    link = normalize(seed_url, link)

                    if link not in seen:
                        seen[link] = depth + 1
                        # if same_domain(seed_url, link):
                        crawl_queue.append(link)

            num_urls += 1
            if num_urls == max_urls:
                break
        else:
            print 'Blocked by robots.txt:', url


SLEEP_TIME = 1

def threaded_crawler(seed_url, delay=5,  user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=60,
                     scrape_callback=None, cache=None):
    """Crawl this website in multiple threads
    """
    #crawl_queue = Queue.deque([seed_url])
    crawl_queue = [seed_url]
    seen = set([seed_url])
    D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)

    def process_queue():
        while True:
            try:
                url = crawl_queue.pop()
            except IndexError:
                break
            else:
                html = D(url)
                if scrape_callback:
                    try:
                        links = scrape_callback(url, html) or []
                    except Exception as e:
                        print 'Error in callback for: {}: {}'.format(url, e)
                    else:
                        for link in links:
                            link = normalize(seed_url, link)
                            print link
                            if link not in seen:
                                seen.add(link)
                                crawl_queue.append(link)

    threads = []
    while threads or crawl_queue:
        for thread in threads:
            if not thread.is_alive():
                threads.remove(thread)
        while len(threads) < max_threads and crawl_queue:
            thread = threading.Thread(target=process_queue)
            thread.setDaemon(True)
            thread.start()
            threads.append(thread)
        time.sleep(SLEEP_TIME)


if __name__ == "__main__":
    # link_crawler('http://example.webscraping.com', '/(index|view)', delay=0, num_retries=1, user_agent='BadCrawler')
    import time
    start = time.time()
    link_crawler('http://example.webscraping.com', '/(index|view)', delay=1, num_retries=5, max_depth=3, user_agent='Baidu', cache=DiskCache(), max_urls=10)
    end = time.time()
    print "* Elapsed time: %3.2f seconds" % (end - start)
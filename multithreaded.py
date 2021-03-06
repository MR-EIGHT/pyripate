import multiprocessing
import os
import concurrent.futures
import threading
from bs4 import BeautifulSoup
import requests
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse


class MultiThreadPyrate:
    counter = 0

    def __init__(self, arguments):
        self.url = arguments.url
        print(self.url)
        self.limit = arguments.number
        self.root_url = '{}://{}'.format(urlparse(self.url).scheme,
                                         urlparse(self.url).netloc)
        self.current_num = 0
        self.path = str(self.url.replace(urlparse(self.url).scheme, '').replace('/', '').replace(':', ''))
        if not os.path.isdir(f"./{self.path}"):
            os.makedirs(f"./{self.path}")

        self.threadLock = threading.Lock()
        self.lock = multiprocessing.Lock()

        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=arguments.parallels)
        self.scraping_queue = Queue()
        self.scraped_urls = set([])
        self.scraping_queue.put(arguments.url)

    def rip(self):

        while self.current_num <= self.limit - 1:
            try:
                current_page = self.scraping_queue.get(timeout=20)

                if current_page not in self.scraped_urls:
                    self.scraped_urls.add(current_page)

                    self.pool.submit(self.ate, current_page)
                    if not (current_page.endswith('.jpg') or current_page.endswith('.png') or current_page.endswith(
                            '.js') or current_page.endswith('.gif') or current_page.endswith(
                        '.css') or current_page.endswith('.jpeg')):
                        with self.threadLock:
                            self.current_num += 1
            except Empty:
                return
            except Exception as e:
                print(e)
                continue
        self.pool.shutdown(wait=True)

    def ate(self, url):

        try:
            content = requests.get(url, timeout=(3, 30))
            self.post_scrape(content)

        except requests.RequestException:
            return

    def post_scrape(self, content):
        if content.status_code == 200:
            # content_type = content.headers['content-type']
            # extension = mimetypes.guess_extension(content_type)
            scheme = urlparse(content.url).scheme
            name = content.url.replace(scheme, '').replace('/', '').replace(':', '').replace('.', '').replace('=',
                                                                                                              '').replace(
                '\\', '').replace('?', '')

            # ext = os.path.splitext(path)[1]
            # print(path)
            with open(
                    # content.url.rsplit('/', 1)[1]  + + ('.html' if not '.' in content.url[-4:] or path == '/' else '')
                    './' + self.path + '/' + str(name),
                    'wb') as file:
                file.write(content.content)
            self.parse_links(content.text)
            # self.scrape_info(content.text)

    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        anchor_tags = soup.find_all('a', href=True)
        source_tags = soup.find_all('img', {"src": True}) + soup.findAll('script', {"src": True})
        css_tags = soup.findAll("link", rel="stylesheet")
        # if len(source_tags + anchor_tags) == 0:
        #     return
        for link in anchor_tags:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)

                if url not in self.scraped_urls:
                    # if '.' in url[-5:] and url[-5:] != '.html':
                    #     self.scraped_urls.add(url)
                    #     self.ate(url)
                    # else:
                    self.scraping_queue.put(url)

        for link in source_tags:
            url = link['src']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
            if url not in self.scraped_urls:
                self.scraped_urls.add(url)
                self.ate(url)

        for link in css_tags:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
            if url not in self.scraped_urls:
                self.scraped_urls.add(url)
                self.ate(url)

import multiprocessing
import os
from multiprocessing import shared_memory
import concurrent.futures
import threading
import time
import argparse
from bs4 import BeautifulSoup
import requests
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse


class pyripate:
    counter = 0

    def __init__(self, arguments):
        self.url = arguments.url
        print(self.url)
        self.limit = arguments.number
        self.root_url = '{}://{}'.format(urlparse(self.url).scheme,
                                         urlparse(self.url).netloc)

        self.path = str(urlparse(self.url).netloc)
        self.path = str(self.url.replace(urlparse(self.url).scheme, '').replace('/', '').replace(':', ''))
        if not os.path.isdir(f".\\{self.path}"):
            os.makedirs(f".\\{self.path}")
        self.threadLock = threading.Lock()
        self.lock = multiprocessing.Lock()

        if arguments.multiprocess:
            self.pool = concurrent.futures.ProcessPoolExecutor(max_workers=arguments.parallels)
            self.scraping_queue = multiprocessing.Queue()
            # shm = multiprocessing.shared_memory.SharedMemory(create=True,size=arguments.number * 20)
            # self.scraped_urls = shm.buf[:] = set()
            self.scraped_urls = multiprocessing.Manager().dict()
            self.scraped_urls['counter'] = 0
            self.scraping_queue.put(arguments.url)


    def rip(self):
        while True and self.scraped_urls.get('counter') <= self.limit:
            try:
                print(f"Current Process: {multiprocessing.current_process().name}\n")
                current_page = self.scraping_queue.get(timeout=20)
                if self.scraped_urls.get(current_page) != 1:
                    print(f"Scraping URL: {current_page}")
                    self.scraped_urls[current_page] = 1
                    with self.pool as pool:
                        pool.submit(self.ate, current_page)
                    with self.lock:
                        self.scraped_urls['counter'] += 1
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

    def ate(self, url):
        print('hey')
        try:
            content = requests.get(url, timeout=(3, 30))
            self.post_scrape(content)

        except requests.RequestException:
            return

    def post_scrape(self, content):
        if content.status_code == 200:
            # content_type = content.headers['content-type']
            # extension = mimetypes.guess_extension(content_type)
            path = urlparse(content.url).path
            # ext = os.path.splitext(path)[1]
            # print(path)
            with open(
                    f"./{self.path.replace('/', '').replace(':', '')}/{content.url.replace('/', '').replace(':', '') + ('.html' if not '.' in content.url[-4:] or path == '/' else '')}",
                    'wb') as file:
                file.write(content.content)
            self.parse_links(content.text)
            # self.scrape_info(content.text)

    def parse_links(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        anchor_tags = soup.find_all('a', href=True)
        source_tags = soup.find_all('img') + soup.find_all('a')
        for link in anchor_tags:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)

                if url not in self.scraped_urls:
                    if '.' not in url[-5:] and url[-5:] != '.html':
                        self.scraping_queue.put(url)
                    else:
                        self.scraped_urls[url] = 1
                        self.ate(url)

        for link in source_tags:
            url = link['src']
            print(url)
            url = urljoin(self.root_url, url)
            if url not in self.scraped_urls:
                self.scraped_urls[url] = 1
                self.ate(url)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="This program downloads and stores any website you want within seconds!")
    parser.add_argument('-u', '--url', required=True,
                        help="URL to begin with.")
    parser.add_argument('-n', '--number', type=int, default='10',
                        help="Maximum number of pages to download.")
    parser.add_argument('-p', '--parallels', type=int, default='5',
                        help="Maximum number of parallel processes / threads to download.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-m', '--multiprocess', action='store_true')
    group.add_argument('-t', '--multithread', action='store_true')

    args = parser.parse_args()

    scrapper = pyripate(args)
    scrapper.rip()
    # scrapper.status()

    print(args)

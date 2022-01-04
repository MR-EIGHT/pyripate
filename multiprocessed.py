import multiprocessing
from multiprocessing import shared_memory
import concurrent.futures
import threading
import time
import argparse
from bs4 import BeautifulSoup
import requests
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse

threadLock = threading.Lock()
lock = multiprocessing.Lock()


class pyripate:
    counter = 0

    def __init__(self, arguments):
        self.url = arguments.url
        self.limit = arguments.number
        self.root_url = '{}://{}'.format(urlparse(self.url).scheme,
                                         urlparse(self.url).netloc)

        self.path = str(urlparse(self.url).netloc)

        if arguments.multiprocess:
            self.pool = concurrent.futures.ProcessPoolExecutor(max_workers=arguments.parallels)
            self.scraping_queue = multiprocessing.Queue()
            # shm = multiprocessing.shared_memory.SharedMemory(create=True,size=arguments.number * 20)
            # self.scraped_urls = shm.buf[:] = set()
            self.scraped_urls = multiprocessing.Manager().dict()

        elif arguments.multithread:
            self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=arguments.parallels)
            self.scraping_queue = Queue()
            self.scraped_urls = set()

    def rip(self):
        while True:
            try:
                print(f"Current Process: {multiprocessing.current_process().name}\n")
                current_page = self.scraping_queue.get(timeout=20)

                if self.scraped_urls.get(current_page) != 1:
                    print(f"Scraping URL: {current_page}")
                    self.scraped_urls[current_page] = 1
                    job = self.pool.submit(self.ate, current_page)
                    job.add_done_callback(self.post_scrape)
                    with lock:
                        if len(self.scraped_urls) == self.limit:
                            self.pool.shutdown(wait=True)
                            return
            except Empty:
                return
            except Exception as e:
                print(e)
                continue

    def ate(self, url):
        try:
            content = requests.get(url, timeout=(3, 30))
            return content
        except requests.RequestException:
            return

    def post_scrape(self, cont):
        content = cont.result()
        if content and content.status_code == 200:
            with open(f"{self.path} / {content.url}", 'w') as file:
                file.write(cont.content)
            self.parse_links(content.text)
            self.scrape_info(content.text)

    def parse_links(self, html):
        soup = BeautifulSoup(html,'html.parser')
        anchor_tags = soup.find_all('a', href=True)
        for link in anchor_tags:
            url = link['href']
            if url.startswith('/') or url.startswith(self.root_url):
                url = urljoin(self.root_url, url)
                if url not in self.scraped_pages:
                    self.crawl_queue.put(url)

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
    pyripate.rip()
    pyripate.status()

    print(args)

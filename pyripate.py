import multiprocessing
from multiprocessing import shared_memory
import concurrent.futures
import threading
import time
import argparse
import bs4 as bs
import requests
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse

threadLock = threading.Lock()


class pyripate:
    counter = 0

    def __init__(self, arguments):
        self.url = arguments.url
        self.limit = arguments.number
        self.root_url = '{}://{}'.format(urlparse(self.url).scheme,
                                         urlparse(self.url).netloc)
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

import mimetypes
import multiprocessing
import os
import random
from multiprocessing import shared_memory
import concurrent.futures
import threading
import time
import argparse
from bs4 import BeautifulSoup
import requests
from queue import Queue, Empty
from urllib.parse import urljoin, urlparse

lock = multiprocessing.Lock()
scraping_queue = multiprocessing.Queue()
scraped_urls = multiprocessing.Manager().dict()
scraped_urls['counter'] = 0

root_url = '{}://{}'.format(urlparse('https://urmia.ac.ir/').scheme,
                            urlparse('https://urmia.ac.ir/').netloc)

def ate(url):
    global scraped_urls, lock, scraping_queue, root_url


    print(scraped_urls['counter'])
    path = str(url.replace(urlparse(url).scheme, '').replace('/', '').replace(':', ''))
    try:
        content = requests.get(url, timeout=(3, 30))
        if content.status_code == 200:
            path = urlparse(content.url).path

            with open(
                    f"./{random.random()}",
                    'wb') as file:
                file.write(content.content)
            html = content.text
            soup = BeautifulSoup(html, 'html.parser')
            print('works1')
            anchor_tags = soup.find_all('a', href=True)
            print('works2')
            for link in anchor_tags:
                url = link['href']
                if url.startswith('/') or url.startswith(root_url):
                    url = urljoin(root_url, url)
                    if scraped_urls.get(url) != 1:
                        print('works4')
                        scraping_queue.put(url)
                        print('bib bib')
    except requests.RequestException:
        return


def run():
    global scraped_urls, lock, scraping_queue, root_url

    scraping_queue.put('https://urmia.ac.ir/')

    limit = 20
    pool = concurrent.futures.ProcessPoolExecutor(max_workers=10)

    while True and scraped_urls.get('counter') <= limit:
        try:
            print(f"Current Process: {multiprocessing.current_process().name}\n")
            current_page = scraping_queue.get(timeout=20)

            if scraped_urls.get(current_page) != 1:
                print(f"Scraping URL: {current_page}")

                scraped_urls[current_page] = 1
                with lock:
                    scraped_urls['counter'] += 1
                pool.submit(ate, current_page)


        except Empty:
            exit(1)
        except Exception as e:
            print(e)
            continue


if __name__ == '__main__':
    run()

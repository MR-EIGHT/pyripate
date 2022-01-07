import concurrent.futures
import multiprocessing
import os
import random
from queue import Empty
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup

lock = multiprocessing.Lock()
scraping_queue = multiprocessing.Queue()
scraped_urls = multiprocessing.Manager().dict()
scraped_urls['counter'] = 0
root_url = None
path = None


def ate(url):
    global scraped_urls, lock, scraping_queue, root_url, path

    try:
        content = requests.get(url, timeout=(3, 30))
        if content.status_code == 200:
            # path = urlparse(content.url).path

            scheme = urlparse(content.url).scheme
            name = content.url.replace(scheme, '').replace('/', '').replace(':', '').replace('.', '').replace('=',
                                                                                                              '').replace(
                '\\', '').replace('?', '')

            with open(
                    './' + path + '/' + str(name),
                    'wb') as file:
                file.write(content.content)
            html = content.text
            soup = BeautifulSoup(html, 'html.parser')
            anchor_tags = soup.find_all('a', href=True)
            source_tags = soup.find_all('img', {"src": True}) + soup.findAll('script', {"src": True})
            css_tags = soup.findAll("link", rel="stylesheet")
            for link in anchor_tags:
                url = link['href']
                if url.startswith('/') or url.startswith(root_url):
                    url = urljoin(root_url, url)
                    if scraped_urls.get(url) != 1:
                        scraping_queue.put(url)

            for link in source_tags:
                url = link['src']
                if url.startswith('/') or url.startswith(root_url):
                    url = urljoin(root_url, url)
                if scraped_urls.get(url) != 1:
                    scraped_urls[url] = 1
                    ate(url)

            for link in css_tags:
                url = link['href']
                if url.startswith('/') or url.startswith(root_url):
                    url = urljoin(root_url, url)
                if scraped_urls.get(url) != 1:
                    scraped_urls[url] = 1
                    ate(url)

    except requests.RequestException:
        return


def run(args):
    global scraped_urls, lock, scraping_queue, root_url, path
    limit = args.number
    workers = args.parallels
    root_url = '{}://{}'.format(urlparse(args.url).scheme,
                                urlparse(args.url).netloc)

    path = str(args.url.replace(urlparse(args.url).scheme, '').replace('/', '').replace(':', ''))
    if not os.path.isdir(f"./{path}"):
        os.makedirs(f"./{path}")

    pool = concurrent.futures.ProcessPoolExecutor(max_workers=workers)
    scraping_queue.put(args.url)
    while scraped_urls.get('counter') <= limit - 1:
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

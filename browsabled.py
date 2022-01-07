import os
import time
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup


class Browsabled:
    def __init__(self, path, url):
        self.path = path
        self.root_url = '{}://{}'.format(urlparse(url).scheme,
                                         urlparse(url).netloc)

    def make_links_relative(self):
        for file in os.listdir(self.path):
            with open(self.path + '/' + file, 'rb') as f:
                text = f.read()

            soup = BeautifulSoup(text, 'html.parser')
            anchor_tags = soup.find_all('a', href=True)
            source_tags = soup.find_all('img', {"src": True}) + soup.findAll('script', {"src": True})
            css_tags = soup.findAll("link", rel="stylesheet")

            for link in anchor_tags:
                url = link['href']
                urled = url
                if url.startswith('/') or url.startswith(self.root_url):
                    urled = urljoin(self.root_url, url)
                text.replace(url, self.path + '/' + self.__get_file_name__(urled))

            for link in source_tags:
                url = link['src']
                urled = url
                if url.startswith('/') or url.startswith(self.root_url):
                    urled = urljoin(self.root_url, url)
                text.replace(url, self.path + '/' + self.__get_file_name__(urled))

            for link in css_tags:
                url = link['href']
                urled = url
                if url.startswith('/') or url.startswith(self.root_url):
                    urled = urljoin(self.root_url, url)
                text.replace(url, self.path + '/' + self.__get_file_name__(urled))

            with open(self.path + '/' + file, 'wb') as f:
                f.write(text)

    def __get_file_name__(self, url):
        scheme = urlparse(url).scheme
        name = url.replace(scheme, '').replace('/', '').replace(':', '').replace('.', '').replace('=', '').replace('\\',
                                                                                                                   '').replace(
            '?', '')
        return name

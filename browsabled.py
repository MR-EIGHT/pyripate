import os
from bs4 import BeautifulSoup


class Browsabled:
    def __init__(self, path):
        self.path = path

    def make_links_relative(self):
        for file in os.listdir(self.path):
            with open(self.path + file, 'rb') as f:
                text = f.read()
            soup = BeautifulSoup(text, 'html.parser')
            anchor_tags = soup.find_all('a', href=True)
            for link in anchor_tags:
                url = link['href']
                text.replace(url, self.path + '/' + self.__get_file_name__(url))
            with open(self.path + file, 'wb') as f:
                f.write(text)

    def __get_file_name__(self, url):
        return url.rsplit('/', 1)[1]

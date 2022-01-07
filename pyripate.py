import argparse
from urllib.parse import urlparse

from browsabled import Browsabled
from multithreaded import MultiThreadPyrate
import multiprocessed

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

    if args.multithread:
        threaded = MultiThreadPyrate(args)
        threaded.rip()

    elif args.multiprocess:
        multiprocessed.run(args)

    b = Browsabled('./'+str(args.url.replace(urlparse(args.url).scheme, '').replace('/', '').replace(':', '')))
    b.make_links_relative()

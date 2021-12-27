import multiprocessing
import threading
import concurrent.futures
import threading
import time
from concurrent.futures import thread
import argparse

# threadLock = threading.Lock()
#
# counter = 0
#
#
# def mainthing():
#     global counter
#     if counter < 3:
#         with threadLock:
#             counter += 1
#         time.sleep(30)
#
#
# for i in range(10):
#     with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
#         res = [executor.submit(mainthing) for _ in range(10)]
#         while True:
#             if counter >= 3:
#                 # executor._threads.clear()
#                 # concurrent.futures.thread._threads_queues.clear()
#                 executor.shutdown(wait=False, cancel_futures=True)
#                 break
#         print(counter)

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
    print(args)

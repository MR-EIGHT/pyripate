import multiprocessing
import threading
import concurrent.futures
import threading
import time
from concurrent.futures import thread
threadLock = threading.Lock()

counter = 0


def mainthing(some):
    global counter
    with threadLock:
        counter += 1
    time.sleep(10)


with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
    res = [executor.submit(mainthing, 1) for _ in range(10)]
    while True:
        if counter >= 3:
            # executor._threads.clear()
            # concurrent.futures.thread._threads_queues.clear()
            executor.shutdown(wait=False, cancel_futures=True)
            break
    print(counter)

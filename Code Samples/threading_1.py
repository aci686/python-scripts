# !/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import random, threading, time

def send_message(index):
    print('[' + str(index) + '] Start!')

    time.sleep(random.choice([2, 4, 6, 8]))
    print('[' + str(index) + '] End!')

def main():
    ####### Finite/manual threads
    #t1 = threading.Thread(target=send_message, args=(message1,))
    #t2 = threading.Thread(target=send_message, args=(message2,))

    #t1.start()
    #t2.start()
    #t1.join()
    #t2.join()

    # Declare, start and join multiple threads
    threads = []
    for _ in range(10):
        t = threading.Thread(target=send_message, args=(_, ))
        t.start()
        threads.append(t)

    for _ in threads:
        t.join()

if __name__ == '__main__':
    main()

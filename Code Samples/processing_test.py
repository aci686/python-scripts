#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import random, multiprocessing, time, os

def send_message(index):
    print('[' + str(index) + '] Start {}!'.format(os.getpid()))

    time.sleep(random.choice([20, 40, 60, 80]))
    print('[' + str(index) + '] End {}!'.format(os.getpid()))

def main():
    #t1 = threading.Thread(target=send_message, args=(message1,))
    #t2 = threading.Thread(target=send_message, args=(message2,))

    #t1.start()
    #t2.start()
    #t1.join()
    #t2.join()

    processes = []
    for _ in range(10):
        p = multiprocessing.Process(target=send_message, args=(_, ))
        p.start()
        processes.append(p)

    for _ in processes:
        p.join()

if __name__ == '__main__':
    main()

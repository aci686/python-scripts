#!/usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

import socket

host = '127.0.0.1'
port = 4444

def send_message(message):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((host, port))
    s.send(message.encode('ascii'))
    s.close()

def main():
    send_message('Sent traffic!')

if __name__ == '__main__':
    main()

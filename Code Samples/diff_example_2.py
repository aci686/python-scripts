#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# @single_request_timeout.setter

def single_request_timeout(self, value):
    # The timeout blah blah
    if value is not None and value <= 0:
        raise ValueError("single_request_timeout must be positive integer")
    self._single_request_timeout = value

if __name__ == "__main__":
    print("Hello!")

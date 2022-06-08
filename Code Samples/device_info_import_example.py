# ! /usr/bin/env python3

#


__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Use file device_info as source of variables

from device_info import router1

if __name__ == "__main__":
    print(router1)
    print(router1["address"])
    
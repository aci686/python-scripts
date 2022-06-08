# ! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Create class for device
# Instantiate class and print some attributes
# Use external
# Use class function
class device:
    def __init__(self, address, hostname, username, password):
        self.address = address
        self.hostname = hostname
        self.username = username
        self.password = password

    def show_hostname(self):
        print(self.hostname)

if __name__ == "__main__":
    router1 = device("192.168.1.1", "router1", "cisco", "cisco")
    print(router1.username)
    router1.show_hostname()

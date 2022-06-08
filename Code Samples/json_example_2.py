# ! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Read JSON formatted file to a variable
# Print first item in the variable

import json

if __name__ == "__main__":
    with open("json_example_1.json", "r") as read_file:
        data = json.load(read_file)
    print(data["president"][0]["name"])

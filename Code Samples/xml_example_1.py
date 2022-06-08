# ! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Use XMLtoDICT library
# Additional file xml_example_1.xml

import xmltodict

if __name__ == "__main__":
    with open("xml_example_1.xml") as fd:
        doc = xmltodict.parse(fd.read())
    print(doc["mydocument"]["plus"]["#text"])
    print(doc["mydocument"]["plus"]["@a"])
    print(doc["mydocument"]["and"]["many"])
    print(doc["mydocument"]["@has"])
    
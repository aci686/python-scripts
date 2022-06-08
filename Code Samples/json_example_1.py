# ! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Having a JSON "data" variable
# Print first item in the list
# Dump variable to a file

import json
    
data = {
    "president": [
        {
            "name": "Zaphid Beeblebrox",
            "species": "Betelgeusian"
        },
        {
            "name": "Ford Prefect",
            "species": "Betelgeusian"
        }
    ]
}

if __name__ == "__main__":
    print(data["president"][0]["name"])
    with open("json_example_1.json", "w") as write_file:
        json.dump(data, write_file)
        
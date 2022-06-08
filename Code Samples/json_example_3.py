# ! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

# Get JSON file from https://jsonplaceholder.typicode.com/todos
# Dump to variable
# Print some data

import json, requests
from colorama import Fore

if __name__ == "__main__":
    response = requests.get("https://jsonplaceholder.typicode.com/todos")
    todos = json.loads(response.text)
    
    print("There are " + Fore.RED + "{} ".format(len(todos)) + Fore.RESET  + "registers")
    print("First register contains: " + Fore.RED + "{}".format(todos[0]) + Fore.RESET)
    print("Last register contains: " + Fore.RED + "{}".format(todos[-1]) + Fore.RESET)
    print("First " + Fore.RED + "3" + Fore.RESET + " registers are: " + Fore.RED + "{}".format(todos[:3]) + Fore.RESET)
    print("Last " + Fore.RED + "3" + Fore.RESET + " registers are: " + Fore.RED + "{}".format(todos[-3:]) + Fore.RESET)
    print(Fore.RED + "Completed" + Fore.RESET + " register titles are:")
    for todo in todos:
        if todo["completed"]:
            print("Title: " + Fore.RED + "{}".format(todo["title"]) + Fore.RESET)
    
    print(Fore.RED + "Uncompleted" + Fore.RESET + " register titles are:")
    for todo in todos:
        if not todo["completed"]:
            print("Title: " + Fore.RED + "{}".format(todo["title"]) + Fore.RESET)
            
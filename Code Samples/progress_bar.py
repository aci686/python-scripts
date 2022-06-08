#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

#

from tqdm import tqdm
from pyfiglet import Figlet
from time import sleep
from random import randrange

sub_fig = Figlet(font='slant')
print(sub_fig.renderText('Network Bits'))

letters=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',' I',' J', 'K', 'L', 'M', 'O','P', 'Q', 'R', 'S','T', 'U', 'V', 'W', 'X', 'Y', 'Z']
with tqdm(total=100, desc="Reading letters") as pbar:
    for i in range(len(letters)):
        sleep(randrange(3))
        pbar.update(100 / len(letters))
        tqdm.write("Letter read: " + letters[i] + "\n")
        
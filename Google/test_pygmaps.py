#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import pygmaps

def main():
    mymap = pygmaps.maps(10.555273, -5.513500, 14)
    mymap.addpoint(10.541945, -5.493763, '#0000FF')
    mymap.addpoint(10.555273, -5.513733, '#0000FF')
    mymap.addpoint(10.540898, -5.51316, '#0000FF')
    mymap.addpoint(10.535445, -5.505427, '#0000FF')
    mymap.addpoint(10.52855, -5.517937, '#0000FF')
    mymap.addpoint(10.574815, -5.514953, '#0000FF')
    mymap.addpoint(10.54269, -5.497085, '#0000FF')
    mymap.addpoint(10.543012, -5.50607, '#0000FF')
    mymap.draw('mymap.draw.html')

if __name__ == '__main__':
    main()
    
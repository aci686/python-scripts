#! /usr/bin/env python3

#

__author__ = "Aaron Castro"
__author_email__ = "aaron.castro.sanchez@outlook.com"
__author_nick__ = "i686"
__copyright__ = "Aaron Castro"
__license__ = "MIT"

import threading, time, sys

def load_animation(done):
    print('\x1b[?25l') # Hide cursor

    # String to be displayed when the application is loading
    load_str = 'Loading...'
    ls_len = len(load_str)

    # String for creating the rotating line
    animation = "|/-\\"
    anicount = 0
      
    # pointer for travelling the loading string
    i = 0                     
  
    while True:
        if done():
            break
        # used to change the animation speed
        # smaller the value, faster will be the animation
        time.sleep(0.1) 
                              
        # converting the string to list
        # as string is immutable
        load_str_list = list(load_str) 
          
        # x->obtaining the ASCII code
        x = ord(load_str_list[i])
          
        # y->for storing altered ASCII code
        y = 0                             
  
        # if the character is "." or " ", keep it unaltered
        # switch uppercase to lowercase and vice-versa 
        if x != 32 and x != 46:             
            if x>90:
                y = x-32
            else:
                y = x + 32
            load_str_list[i]= chr(y)
          
        # for storing the resultant string
        res =''             
        for j in range(ls_len):
            res = res + load_str_list[j]
              
        # displaying the resultant string
        sys.stdout.write('\r[' + animation[anicount] + '] ' + res)
        sys.stdout.flush()
  
        # Assigning loading string
        # to the resultant string
        load_str = res

        anicount = (anicount + 1) % 4
        i =(i + 1) % ls_len

    sys.stdout.write('\r')
    sys.stdout.flush()
    sys.stdout.write('\x1b[?25h') # Show cursor

def main():
    done = False
    anim = threading.Thread(target=load_animation, args=(lambda:done, ))
    anim.start()
    # Long lasting function goes here
    done = True
    anim.join()
    
if __name__ == '__main__':
    main()

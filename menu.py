#!/usr/bin/python3
import sys
import os
import yaml
from display import Display

def main():

    # load the menu
    with open(r'./menu.yaml') as file:
        # The FullLoader parameter handles the conversion from YAML
        # scalar values to Python dictionary format
        config = yaml.load(file, Loader=yaml.FullLoader)

    menu = config["root"]
    items = []
    for item in menu:
        items.append(item)

    #initialize Display
    disp: Display = Display()
    disp.Draw(items)

try:
    if __name__ == '__main__':
        main()
except:
   print("Oops!",sys.exc_info()[0],"occured.")
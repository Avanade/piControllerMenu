# Copyright (c) 2019 Avanade
# Author: Thor Schueler
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
import sys
import time
import yaml
import logging
from display import Display, CONFIRM_OK, CONFIRM_CANCEL
from navigation import Navigation
from command import Command, COMMAND_SHELL, COMMAND_BUILTIN

class ControllerMenu(object):
    """
        Main class of the PI Controller Menu. Handles loading and running the menu and commands. 
    """
    def __init__(self, config = "./controllerMenu.yaml"):
        """
            Constructor. Creates a new instance of the ContollerMenu class. 
            Paramters: 
                config:     str
                            Name of the config file for the controller menu. Defaults to ./controllerMenu.yaml. 
        """
        self.__configFile = config
        self.__config = None
        self.__rootMenu = None
        self.__commands = {}
        self.__currentMenu = None
        self.__breadcrumb = [""]
        self.__load()

    def Run(self):
        """
            Main loop. Does not really do anything other than keeping the main thread alive. 
        """
        while True:
            time.sleep(120)

    def __load(self):
        """
            Loads the controller menu configuration and boots the menu. 
        """
        # load the menu
        with open(self.__configFile) as file:
            # The FullLoader parameter handles the conversion from YAML
            # scalar values to Python dictionary format
            self.__config = yaml.load(file, Loader=yaml.FullLoader)

        self.__rootMenu = self.__config["root"]
        self.__currentMenu = self.__rootMenu
        items = []
        for item in self.__currentMenu: items.append(item)

        # initialize Display
        self.__disp: Display = Display()
        self.__disp.Items = items
        self.__disp.ResetMenu()
        self.__disp.SelectCallback = self.__processSelectEvent
        self.__disp.UpCallback = self.__processBreadcrumbEvent
        self.__disp.ConfirmCallback = self.__processConfirmEvent

        # load configured commands
        for item in self.__config["commands"]:
            self.__commands[item] = Command.FromJSON(self.__config["commands"][item])
            self.__commands[item].SpinHandler = self.__disp.Spinner
            if self.__commands[item].Type == COMMAND_SHELL: 
                    self.__commands[item].OutputHandler = self.__disp.DrawOutput
            if self.__commands[item].Confirm == True:
                    self.__commands[item].ConfirmationHandler = self.__disp.DrawConfirmation

        # initialize Navigation buttons
        self.__nav: Navigation = Navigation(self.__disp.ProcessNavigationEvent)

    def __processSelectEvent(self, selectIndex: int, selectItem: str):
        """
            Delegate to respond to a select event on the controller tactile select button. Invokes either
            navigation to a submenu or command execution. 
            Paramters: 
                selectedIndex:  int
                                Index of the menu item selected.
                selectedItem:   str
                                The selected menu item
        """
        items = [".."]
        if type(self.__currentMenu[selectItem]) is str:
            logging.info("Execute {self.__currentMenu[selectItem]}")
            self.__commands[self.__currentMenu[selectItem]].Run(display=self.__disp)
        else:
            logging.info("Load {self.__currentMenu[selectItem]}")
            self.__currentMenu = self.__currentMenu[selectItem]
            self.__breadcrumb.append(selectItem)
            for item in self.__currentMenu: items.append(item)
            self.__disp.Items = items

    def __processBreadcrumbEvent(self):
        """
            Delegate to respond to the navigate uo event on the controller tactile Up button. Loads the 
            previous menu. 
        """
        items = []
        self.__breadcrumb.pop()
        for level in self.__breadcrumb:
            if level == "": self.__currentMenu = self.__rootMenu
            else: 
                self.__currentMenu = self.__currentMenu[level]
                items.append("..")
        for item in self.__currentMenu: items.append(item)
        self.__disp.Items = items

    def __processConfirmEvent(self, command:Command, confirmState: int):
        """
            Delegate to respond to the confirmation event from the confirmation screen. Depending on event state, 
            either reloads the previous menu (confirmState==CONFIRM_CAMCEL) or run the commmand (CONFIRM_OK)
            Parameters:
                command:        Command
                                The command to run if confirmed
                confirmState:   int
                                The confirm state. Either CONFIRM_OK or CONFIRM_CANCEL
        """
        if confirmState == CONFIRM_CANCEL: self.__disp.DrawMenu()
        else:
            command.Run(display=self.__disp, confirmed=CONFIRM_OK)




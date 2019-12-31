# Copyright (c) 2018 Avanade
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
#
# pylint: disable=C0103
import time
import threading
from PIL import Image, ImageDraw, ImageFont
from navigation import UP_CLICK, DOWN_CLICK, LEFT_CLICK, RIGHT_CLICK, SELECT_CLICK
from . import LCD, LCD_Config

MODE_MENU = 0
MODE_CONFIRM = 1
MODE_OUTPUT = 2
MODE_EXTERNAL = 3
CONFIRM_CANCEL = 0
CONFIRM_OK = 1
MSG_OK = "OK"
MSG_CANCEL = "CANCEL"
MSG_RUN = "You are about to run"
MSG_PROCEED = "Proceed?"
MSG_RESULTS = "'%s'"
MSG_CODE = "Return Code: %x"
MSG_OUTPUT = "Output:"


class Display(object):
    """
        The Display class represent a TFT on which to display the menu
    """

    #region  Constructors
    def __init__(self):
        """
            Creates a new instance of hte Display class
        """
        self.__mode = MODE_MENU
        self.__disp = LCD.LCD()                                             # setup LCD
        self.__scanDirection = LCD.D2U_L2R
        self.__disp.LCD_Init(self.__scanDirection)
        self.__disp.LCD_Clear(0x0)
        self.__width = self.__disp.LCD_Dis_Column
        self.__height = self.__disp.LCD_Dis_Page

        self.__scrollStartIndex = 0
        self.__scrollDown = False
        self.__scrollUp = False
        self.__selectedIndex = -1
        self.__maxIndex = -1
        self.__selectCallback = None
        self.__upCallback = None
        self.__confirmCallback = None
        self.__image = Image.new('RGB', (self.__width, self.__height))      # setup canvas
        self.__draw = ImageDraw.Draw(self.__image)                          # Get drawing object
        
        self.__spinnerThread = None
        self.__stopSpinner = False
        self.__stopCommand = False

        self.__confirmCommand = None
        self.__confirmState = CONFIRM_CANCEL

        # Load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        self.__font = ImageFont.truetype('display/Roboto-Regular.ttf', 12)
        self.__textColor = "#00FF00"
        self.__selectedColor = "#FFFFFF"
        self.__navigationColor = "#00FF00"
        self.__padding = 10
        self.__items = []
        self.DrawMenu()
    #endregion

    #region Property implementations
    @property
    def Items(self):
        """ Gets the list of current menu items. """
        return self.__items

    @Items.setter
    def Items(self, items):
        """ Sets the list of current menu items and intiates a redraw of the menu. """
        self.__items = items
        self.__scrollDown = False
        self.__scrollUp = False
        self.__scrollStartIndex = 0
        self.__selectedIndex = 0
        self.__maxIndex = len(items)
        self.DrawMenu()      

    @property
    def ConfirmCallback(self) -> callable:
        """ 
            Gets the delegate for the confirmation callback. This callback is invoked once a user 
            has confirmed the execution of a command
        """
        return self.__confirmCallback  

    @ConfirmCallback.setter
    def ConfirmCallback(self, callback):
        """
            Sets the delegate for the confirmation callback. The delegate is expected to have the following signature
            (command:Command, confirmState: int) -> None
        """
        self.__confirmCallback = callback

    @property
    def Dimensions(self) -> (int, int):
        """ Gets the dimensions of the display """
        return (self.__width, self.__height)

    @property
    def Font(self) -> ImageFont:
        """ Gets the active display font """
        return self.__font

    @property
    def SelectCallback(self) -> callable:
        """ Gets the delegate invoked when the user selects a menu item. """
        return self.__selectCallback  

    @SelectCallback.setter
    def SelectCallback(self, callback):
        """ 
            Sets the delegate invoked when the user selects a menu item. The delegate should have the following signature
            (selectIndex: int, selectItem: str) -> None       
        """
        self.__selectCallback = callback

    @property
    def StopCommand(self) -> bool:
        """ 
            Gets the stop command flag. This is used for built-in commands only and signifies that 
            command execution should be stopped. 
        """
        return self.__stopCommand

    @StopCommand.setter
    def StopCommand(self, val):
        """ 
            Sets the stop command flag. This is used for built-in commands only and signifies that 
            command execution should be stopped. 
        """
        self.__stopCommand = val

    @property
    def UpCallback(self) -> callable:
        """ Gets the delegate invoked when the user navigates up the menu structure. """
        return self.__upCallback  

    @UpCallback.setter
    def UpCallback(self, callback):
        """ 
            Sets the delegate invoked when the user navigates up the menu structure. The delegate shold have the following signature
            () -> None    
        """        
        self.__upCallback = callback
    #endregion

    #region Public method implementations
    def DrawConfirmation(self, command=None, state = CONFIRM_CANCEL):
        """
            Draws the confirmation dialog on the display. 
            Parameters:
                command:    Command
                            A reference to the command for which to display the confirmation
                state:      int
                            The current confirmation state. Used to set the focus for the OK/Cancel buttone. 
                            Pass COMFIRM_CANCEL to put the focus on the Cancel button, CONFIRM_OK to put the 
                            focus on the Ok button.  
        """
        self.__mode = MODE_CONFIRM
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        if command != None: self.__confirmCommand = command
        self.__confirmState = state
        x = self.__padding
        y = self.__padding
        text = ""
        messages = []
        if self.__confirmCommand != None: 
            messages.append(MSG_RUN)
            messages.append("'%s'" %self.__confirmCommand.Command)
        messages.append(MSG_PROCEED)
        for message in messages: text += message + "\n"

        z = self.__draw.multiline_textsize(text, font=self.__font, spacing=10)
        x = (self.__width - z[0])/2
        c1 = [(10, self.__height-40), (self.__width/2 - 10, self.__height-15)]
        c2 = [(self.__width/2 + 10, self.__height-40), (self.__width - 10, self.__height-15)]
        c3 = (self.__width/4 - self.__draw.textsize(MSG_OK, font=self.__font)[0]/2  , self.__height-35)
        c4 = (3*self.__width/4 - self.__draw.textsize(MSG_CANCEL, font=self.__font)[0]/2, self.__height-35)
        self.__draw.multiline_text((x, y), text, font=self.__font, spacing=10, fill=self.__textColor, align="center")
        self.__draw.rectangle(c1, fill=self.__selectedColor if state==CONFIRM_OK else self.__textColor)
        self.__draw.rectangle(c2, fill=self.__selectedColor if state==CONFIRM_CANCEL else self.__textColor)
        self.__draw.text(c3, MSG_OK, font=self.__font, fill="#000000")
        self.__draw.text(c4, MSG_CANCEL, font=self.__font, fill="#000000")
        self.__disp.LCD_ShowImage(self.__image)

    def DrawImage(self, image:Image):
        """
            Draws an image onto the display. Used mostly for built-in commands 
            Parameters:
                image:  Image
                        Reference to an Image object containing the image to be drawn. 
        """
        self.__mode = MODE_EXTERNAL
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        self.__disp.LCD_ShowImage(image)

    def DrawMenu(self, items:list=None):
        """
            Draws a menu based on the items contained in Display.Items. Setting Display.Items will implicitely 
            call this method, so it should only be necessary to call this explicitely if the display has been 
            changed by the user since it was last drawn. 
            Parameters:
                items:      list(str)
                            Optional. A list of items to be used for the menu. If not specified, the list currently 
                            contained in Display.Items will be used. If specified, the supplied list will be stored in 
                            Display.Items. 
        """
        self.__mode = MODE_MENU
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)

        x = self.__padding
        y = self.__padding
        if items != None: self.__items = items
        self.__scrollDown = False
        self.__scrollUp = self.__scrollStartIndex > 0
        idx = self.__scrollStartIndex
        while idx < len(self.__items):
            item = self.__items[idx]
            __y = self.__font.getsize(item)[1]
            if y + __y > self.__height: 
                self.__scrollDown = True
                break

            self.__draw.text((x, y), item, font=self.__font, 
                fill= self.__selectedColor if idx == self.__selectedIndex else self.__textColor)
            idx += 1
            y += __y + self.__padding
        self.__maxIndex = idx
        self.__drawScrollArrows()
        self.__disp.LCD_ShowImage(self.__image)

    def DrawOutput(self, command:str, code:int, message:str=""):
        """
            Draws the output of a command (or any string, really).
            Parameters:
                command:    str
                            Contains the name (command line) of the command whose output is shown
                code:       int
                            The command exit code.
                message:    str
                            Optional. Output to display.  
        """
        self.__mode = MODE_OUTPUT
        self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
        x = self.__padding
        y = self.__padding
        self.__draw.text((x, y), MSG_RESULTS %command, font=self.__font, fill=self.__textColor)
        y += self.__font.getsize(MSG_RESULTS)[1] + self.__padding
        self.__draw.text((x, y), MSG_CODE %code, font=self.__font, fill=self.__textColor)                
        y += self.__font.getsize(MSG_CODE)[1] + self.__padding 
        if message != "":
            self.__draw.text((x, y), MSG_OUTPUT, font=self.__font, fill=self.__textColor)
            y += self.__font.getsize(MSG_OUTPUT)[1] + self.__padding
            self.__draw.multiline_text((x + self.__padding,y), message, fill=self.__textColor)

        c1 = [(self.__width/2 + 10, self.__height-40), (self.__width - 10, self.__height-15)]
        c2 = (3*self.__width/4 - self.__draw.textsize(MSG_OK, font=self.__font)[0]/2, self.__height-35)
        self.__draw.rectangle(c1, fill=self.__textColor)
        self.__draw.text(c2, MSG_OK, font=self.__font, fill="#000000")        
        self.__disp.LCD_ShowImage(self.__image)

    def Spinner(self, run=True):
        """
            Loads the spinner screen while a command executes. This will start a background thread when invoked with run=True and 
            derminate the thread (and spinner) when invoked with run=False
            Parameters:
                run:    bool
                        Optional. Pass True to start the spinner, false to derminate the spinner.
        """
        if run==True:
            self.__stopSpinner = False
            self.__spinnerThread = threading.Thread(target=self.__drawSpinner, name="spinner", args=(lambda : self.__stopSpinner, ))
            self.__spinnerThread.start()
        else:
            if self.__spinnerThread is None: return
            self.__stopSpinner = True
            self.__spinnerThread.join()

    def ProcessNavigationEvent(self, eventType):
        """
            Delegate called by the Navigation model when a navigation event occurs on the GPIO. Handles 
            corresponding invokation of the various display draw and/or command execution delegates. 
            Parameters:
                eventType:  int
                            The type of event that occured. One of the following:
                                DOWN_CLICK
                                UP_CLICK
                                LEFT_CLICK
                                RIGHT_CLICK
                                SELECT_CLICK
        """
        if eventType is DOWN_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == self.__maxIndex-1 and self.__scrollDown is False: return
            if self.__selectedIndex == self.__maxIndex-1: self.__scrollStartIndex +=1
            self.__selectedIndex += 1
            self.DrawMenu()
            return

        if eventType is UP_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == 0 and self.__scrollUp is False: return
            if self.__selectedIndex == -1: 
                self.__selectedIndex = 0
                self.__scrollStartIndex = 0
            else:
                if self.__selectedIndex == self.__scrollStartIndex: self.__scrollStartIndex -= 1
                self.__selectedIndex -= 1
            self.DrawMenu()
            return

        if eventType is LEFT_CLICK and self.__mode == MODE_MENU and self.__upCallback: 
            self.__upCallback()
            return
        if eventType is LEFT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_OK)
            return
        if eventType is RIGHT_CLICK and self.__mode == MODE_CONFIRM: 
            self.DrawConfirmation(state=CONFIRM_CANCEL)
            return

        if eventType is SELECT_CLICK and self.__mode == MODE_MENU:
            if self.__selectedIndex == 0 and self.__items[0] == ".." and self.__upCallback:
                self.__upCallback()
            elif self.__selectCallback and self.__selectedIndex > -1: 
                self.__selectCallback(self.__selectedIndex, self.__items[self.__selectedIndex])
            return
        if eventType is SELECT_CLICK and self.__mode == MODE_CONFIRM and self.__confirmCallback:
            self.__confirmCallback(self.__confirmCommand, self.__confirmState)
            return
        if eventType is SELECT_CLICK and self.__mode == MODE_OUTPUT:
            self.DrawMenu()
            return
        if self.__mode == MODE_EXTERNAL and (eventType is SELECT_CLICK or eventType is LEFT_CLICK):
            self.__stopCommand = True
            return

    def ResetMenu(self):
        """
            Resets the current menu to an unselected state.
        """
        self.__selectedIndex = -1
        self.DrawMenu()
    #endregion

    #region Private method implementations
    def __drawScrollArrows(self):
        """
            Handles drawing of the Scroll Arrows for the menu as needed
        """
        if self.__scrollDown: 
            self.__draw.polygon([
                (self.__width-5, self.__height-10),
                (self.__width-15, self.__height-10),
                (self.__width-10, self.__height-5)
            ], fill=self.__navigationColor, outline=self.__navigationColor)
        if self.__scrollUp:
            self.__draw.polygon([
                (self.__width-5, 10),
                (self.__width-15, 10),
                (self.__width-10, 5)
            ], fill=self.__navigationColor, outline=self.__navigationColor)

    def __drawSpinner(self, stop: callable):
        """
            Thread entry point for the spinner thread started by Display.Spinner()
            Parameters:
                stop:   callable
                        A delegate called to determine whether to terminate the spinner thread. The delegate is 
                        expected to return a boolean: () -> bool. If the delegate returns True, teh spinner thread
                        will terminate. If the delegate returns False, the spinner will continue. The delegate is 
                        evaluated roughly every 2-3ms
        """
        box = [(self.__width - self.__height)/2+25, 25, (self.__width + self.__height)/2-25, self.__height-25]
        while True:
            if stop() : break
            deg = 1
            self.__draw.rectangle((0, 0, self.__width, self.__height), outline=0, fill=0)
            while deg<=360: 
                if stop(): break
                self.__draw.pieslice(box, -90, -90+deg, outline=self.__textColor, fill=self.__textColor)
                self.__disp.LCD_ShowImage(self.__image)
                deg += 1
                time.sleep(0.001)
        self.__draw.pieslice(box, -90, 270, outline=self.__textColor, fill=self.__textColor)
        self.__disp.LCD_ShowImage(self.__image)
    #endregion

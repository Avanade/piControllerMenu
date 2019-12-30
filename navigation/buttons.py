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
import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import logging

#region Globals
GPIO_UP = 17
GPIO_DOWN = 5
GPIO_LEFT = 6
GPIO_RIGHT = 22
GPIO_SELECT = 18
DEBOUNCE = 250

UP_CLICK = 0
DOWN_CLICK = 1
LEFT_CLICK = 2
RIGHT_CLICK = 3
SELECT_CLICK = 4
#endregion

class Navigation(object):
    '''
        The Navigation class implments the interaction with the GPIO driven tactile 
        buttons. It configures the appropriate GPIO pints and setsup the callback for 
        when a button is pressed
    '''
    def __init__(self, 
            callback: callable,
            pins: list=[GPIO_UP, GPIO_DOWN, GPIO_LEFT, GPIO_RIGHT, GPIO_SELECT], 
            debounce: int=DEBOUNCE):
        '''
            Constructor - Creates a new instance of the Navigation class.
            Parameters:
                pins :      [int], optional
                            Sepcify the GPIO pins that connect the tactile buttons: [up, down, left, right, select]. The defaults are
                            [17, 5, 6, 22, 18]
                debounce:   int, optional
                            Specify a debounce time to prevent multiple firings when a button is clicked. The default is 250ms 
        '''
        self.__pins = pins
        self.__debounce = debounce
        self.__callback = callback
        GPIO.setwarnings(False)                                     # Ignore warning for now
        GPIO.setmode(GPIO.BCM)                                      # Use physical pin numbering
        for pin in self.__pins:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)    # Set pin to be an input pin and set initial value to be pulled low (off)
            GPIO.add_event_detect(pin, GPIO.RISING,                 # Setup event on pin 10 rising edge
                callback=self.__buttonPressEvent, bouncetime=self.__debounce)

    def __buttonPressEvent(self, channel: int):
        '''
            Raised when a tactile button on the GPIO channels is pressed. In turn raises the callback passed into the constructor with 
            the argument UP_ClICK, DOWN_CLICK, LEFT_CLICK, RIGHT_CLICK, SELECT_CLICK as appropriate. 
            Parameters:
                channel:    int
                            The GPIO channel on which the click occured. 
        '''
        clickType = "unknown"
        if(channel == self.__pins[0]): clickType = "up"
        if(channel == self.__pins[1]): clickType = "down"
        if(channel == self.__pins[2]): clickType = "left"
        if(channel == self.__pins[3]): clickType = "right"
        if(channel == self.__pins[4]): clickType = "select"  
        logging.info(f"Navigation event received on channel: {channel}; interpreted as '{clickType}' click")

        if(channel == self.__pins[0]): self.__callback(UP_CLICK)
        elif(channel == self.__pins[1]): self.__callback(DOWN_CLICK)
        elif(channel == self.__pins[2]): self.__callback(LEFT_CLICK)
        elif(channel == self.__pins[3]): self.__callback(RIGHT_CLICK)
        elif(channel == self.__pins[4]): self.__callback(SELECT_CLICK)
        else: self.__callback(-1)

    def __del__(self):
        '''
            Destructor - cleans up GPIO resources when the object is destroyed. 
        '''
        GPIO.cleanup()                                              # Clean up


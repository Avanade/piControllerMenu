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
import time
import subprocess
import threading
from abc import ABC, abstractmethod
from display import Display
from PIL import Image, ImageDraw, ImageFont

class BuiltInCommand(ABC):
    '''
        The BuiltInCommand class implments the abstract base class for the various built-in 
        commands of the PI Menu
    '''

    def __init__(self, disp: Display):
        '''
            Constructor - Creates a new instance of the BuiltInCommand class.
            Parameters:
                disp :      Display
                            An instance of the display object representing the screen.
        '''
        self._disp: Display = disp
        self._image = Image.new('RGB', self._disp.Dimensions)
        self._canvas = ImageDraw.Draw(self._image)
        self._output:list = []
        self._padding = 10
        self.__runThread = None
        super().__init__()

    @property
    def Commands(self) -> list:
        """ Gets the list of shell commands to run for the built-in command. """
        return []

    def Run(self, stop: callable, completed: callable = None):
        '''
            Call this to run the sysinfo command. This will start a background thread and immidiately return.
            Parameters:
                stop :      Callable
                            Function to be called periodically to evaluate whether command execution
                            should stop. This method should return True to exit the command, False to keep 
                            running the command.The Function does not take any arguments.  
                completed:  Callable
                            Function to be called upon completion of the command (after stop evaluates to True). 
                            The function is not expected to take any arguments or return a value.  
        '''
        self.__runThread = threading.Thread(target=self.__run, name="runThread", args=(stop, completed))
        self.__runThread.start()

    @abstractmethod
    def _draw(self):
        '''
            Abstract for drawing the screen for the display of the built-in command. To be implemented 
            in derived classes
        '''
        pass

    def _getData(self):
        '''
            Gets the data for command by calling various shell commands defined in BuiltInCommand.commands
        '''
        self._output = []
        for command in self.Commands:
            o = subprocess.check_output(command, shell=True).decode()
            m = list(filter(None, o.split("__br__")))
            self._output += m

    def __run(self, stop: callable, complete: callable):
        '''
            Background thread entry point for the command.
            Parameters
                stop :      Callable
                            Function to be called periodically to evaluate whether command execution
                            should stop. This method should return True to exit the command, False to keep 
                            running the command.The Function does not take any arguments.  
                completed:  Callable
                            Function to be called upon completion of the command (after stop evaluates to True). 
                            The function is not expected to take any arguments or return a value.  
        '''
        while True:
            self._getData()
            self._draw()
            if stop(): break
            time.sleep(1)
        self._disp.StopCommand = False      # this is necessary to reset the stop command flag, unfortunately.
                                            # got to look for a better way, but for now it will do.  
        self._disp.DrawMenu()
        if complete is not None: complete()

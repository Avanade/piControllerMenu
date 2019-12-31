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
import subprocess
from builtin import BuiltInCommand
from display import Display
from PIL import Image, ImageDraw, ImageFont

class NetInfo(BuiltInCommand):
    '''
        The NetInfo class implements a second by second update on network statistics for the PI Menu
    '''
    def __init__(self, disp: Display):
        '''
            Constructor - Creates a new instance of the NetInfo class.
            Parameters:
                disp :      Display
                            An instance of the display object representing the screen.
        '''
        super().__init__(disp)

    @property
    def Commands(self) -> list:
        """ Gets the list of shell commands to run for the netInfo command. """
        return [
            "ip -o link | awk '/ether/ {printf \"%s\\n  status: %s\\n  %s\\n\", $2, $9, $17}'"
        ]

    def _draw(self):
        '''
            Draws the screen for the display of the system information. 
        '''
        self._canvas.rectangle([(0, 0), self._disp.Dimensions], outline=0, fill=(0, 0, 0))
        y = self._padding 
        color="#00ff00"
        for idx, val in enumerate(self._output):
            self._canvas.text((self._padding, y), val, font=self._disp.Font, fill=color)
            y += self._disp.Font.getsize(val)[1]
            y += self._padding
        self._disp.DrawImage(self._image)

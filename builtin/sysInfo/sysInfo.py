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
from builtin import BuiltInCommand
from display import Display
from PIL import Image, ImageDraw, ImageFont

class SysInfo(BuiltInCommand):
    '''
        The SysInfo class implments a second by second update on vital system statistics for the PI Menu
    '''

    commands = [
        "hostname -I | cut -d\' \' -f1 | awk \'{printf \"IP: %s\", $(0)}\'",
        "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'",
        "free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'",
        "df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'",
        "cat /sys/class/thermal/thermal_zone0/temp |  awk \'{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}\'"
    ]

    def __init__(self, disp: Display):
        '''
            Constructor - Creates a new instance of the SysInfo class.
            Parameters:
                disp :      Display
                            An instance of the display object representing the screen.
        '''
        #BuiltInCommand.__init__(self, disp)
        super().__init__(disp)

    def _draw(self):
        '''
            Draws the screen for the display of the system information. 
        '''
        self._canvas.rectangle([(0, 0), self._disp.Dimensions], outline=0, fill=(0, 0, 0))
        y = self._padding 
        for idx, val in enumerate(self._output):
            split = val.split()
            color = "#ffffff"
            if idx==1: color = "#00ff00" if float(split[len(split)-1]) < 0.25 else "#ffff00" if float(split[len(split)-1]) < 0.75 else "#ff0000"
            if idx==2: color = "#00ff00"
            if idx==3: color = "#00ff00"
            if idx==4: color = "#00ff00" if float(split[len(split)-2]) < 50 else "#ffff00" if float(split[len(split)-2]) < 60 else "#ff0000"  
            self._canvas.text((self._padding, y), val, font=self._disp.Font, fill=color)
            y += self._disp.Font.getsize(val)[1]
            y += self._padding
        self._disp.DrawImage(self._image)

    def _getData(self):
        '''
            Gets the data for sysInfo by calling various shell commands defined in SysInfo.commands
        '''
        self._output = []
        for idx, command in enumerate(SysInfo.commands):
            o = subprocess.check_output(command, shell=True).decode()
            self._output.append(subprocess.check_output(command, shell=True).decode())

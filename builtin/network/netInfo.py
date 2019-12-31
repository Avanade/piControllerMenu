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
        self.__network = {}

    @property
    def Commands(self) -> list:
        """ Gets the list of shell commands to run for the netInfo command. """
        return [
            "ip -o link | awk '/ether/ {printf \"%s %s\\n  %s__br__\", $2, $9, $17}'",
            "ip -o addr show | awk '$0 !~ /host/ {printf \"%s: %s__br__\", $2, $4}'"
        ]

    def _draw(self):
        '''
            Draws the screen for the display of the network information. 
        '''
        self._canvas.rectangle([(0, 0), self._disp.Dimensions], outline=0, fill=(0, 0, 0))
        y = self._padding
        x = self._padding + 5
        for name in self.__network:
            iface = self.__network[name]
            color="#00ff00" if iface["status"] == "UP" else "#ffff00"
            self._canvas.text((self._padding, y), f"{name} {iface['status']}", font=self._disp.Font, fill=color)
            y += self._canvas.textsize(f"{name} {iface['status']}", font=self._disp.Font)[1]
            self._canvas.text((x, y), f"mac: {iface['mac']}", font=self._disp.Font, fill=color)
            y += self._canvas.textsize(f"mac: {iface['mac']}", font=self._disp.Font)[1] +3
            for ip in iface["ip"]:
                s = self._canvas.textsize(ip, font=self._disp.SmallFont)
                if s[0] < self._disp.Dimensions[0] - x: 
                    self._canvas.text((x, y), ip, font=self._disp.SmallFont, fill=color)
                    y += s[1] + 3
                else:
                    #likely an IP6 address that is too long. we'll split it into mutliple lines along the colons
                    idx = len(ip)
                    while ((self._canvas.textsize(ip[:idx], font=self._disp.SmallFont)[0] > 
                            self._disp.Dimensions[0] - 2*x) and idx != -1):
                        idx = ip.rfind(":", 0, idx)    
                    for i, p in enumerate([ip[:idx+1], ip[idx+1:]]):    
                        self._canvas.text((x if i ==0 else 2*x, y), p, font=self._disp.SmallFont, fill=color)
                        y += s[1] + 3
            y += self._padding
        self._disp.DrawImage(self._image)

    def _getData(self):
        '''
            Gets the data for network information by calling various shell commands defined in BuiltInCommand.commands
        '''
        self._output = []
        for idx, command in enumerate(self.Commands):
            o = subprocess.check_output(command, shell=True).decode()
            for val in list(filter(None, o.split("__br__"))):
                a = val.split()
                if idx==0:
                    # a[0] -> interface name, a[1] -> status, a[2] -> mac
                    self.__network[a[0]] = {}
                    self.__network[a[0]]["status"] = a[1]
                    self.__network[a[0]]["mac"] = a[2]
                    self.__network[a[0]]["ip"] = []
                if idx==1 and a[0] in self.__network:
                    # a[0] -> interface name, a[1] -> ip 
                    # there can be more than one IP address (one ip4 and mutliple ip6) per interface
                    # not all interfaces have an IP, only interfaces that are UP do
                    self.__network[a[0]]["ip"].append(a[1])


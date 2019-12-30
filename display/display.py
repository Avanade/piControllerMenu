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
from PIL import Image, ImageDraw, ImageFont
from . import LCD, LCD_Config

"""
    The Display class represent a TFT on which to display the menu
"""
class Display(object):

    def __init__(self):
        self.disp = LCD.LCD()                       # setup LCD
        self.scanDirection = LCD.L2R_U2D  
        self.disp.LCD_Init(self.scanDirection)
        self.disp.LCD_Clear(0x0)

        self.width = self.disp.LCD_Dis_Column
        self.height = self.disp.LCD_Dis_Page
        self.image = Image.new('RGB', (self.width, self.height))   # setup canvas
        self.draw = ImageDraw.Draw(self.image)                # Get drawing object
        
        # Load a TTF font.  Make sure the .ttf font file is in the
        # same directory as the python script!
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        self.font = ImageFont.truetype('display/Roboto-Regular.ttf', 12)
        self.padding = 10
        self.items = []
        self.Draw(self.items)
    
    def Draw(self, items):
        self.draw.rectangle((0, 0, self.width, self.height), outline=0, fill=0)

        x = self.padding
        y = self.padding
        self.items = items
        for item in self.items:   
            self.draw.text((x, y), item, font=self.font, fill="#00FF00")
            y += self.font.getsize(item)[1]
            y += self.padding
        self.disp.LCD_ShowImage(self.image)
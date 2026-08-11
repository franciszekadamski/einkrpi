#!/usr/bin/python

import copy
import sys
import os
import logging
import time
from PIL import Image, ImageFilter, ImageChops
import imagehash
import mss
import traceback
import numpy

import epd7in5_V2


class EPDX:
    def __init__(self, display_name: str = ':0'):
        self.epd = epd7in5_V2.EPD()
        self.epd.init()
        self.epd.Clear()
        self.display_name = display_name

        self.similarity_threshold = 0.50

        os.environ['DISPLAY'] = self.display_name
        if 'XAUTHORITY' not in os.environ:
            os.environ['XAUTHORITY'] = f'{os.environ["HOME"]}/.Xauthority' 

        self.capture_x11_frame()
        self.process_image()

        self.previous_image = Image.new('1', (self.epd.width, self.epd.height), 255) 


    def spin(self):
        while True:
            self.capture() 


    def capture(self):
        self.capture_x11_frame()
        self.process_image()
        similarity = self.similarity()  

        if 0.6 <= similarity < 1.0:
            self.display_image_partial()
        elif similarity < 0.6:
            self.display_image()
        else:
            return

    def display_image(self):
        self.epd.init()
        self.epd.display(self.epd.getbuffer(self.image))
        self.epd.sleep()
        self.previous_image = copy.copy(self.image)


    def display_image_fast(self):
        self.epd.init_fast()
        self.epd.display(self.epd.getbuffer(self.image))
        self.previous_image = copy.copy(self.image)


    def display_image_partial(self):
        self.epd.init_part()
        self.epd.display_Partial(self.epd.getbuffer(self.image), 0, 0, self.epd.width, self.epd.height)
        self.previous_image = copy.copy(self.image)


    def get_differences_bounding_box_and_region(self):
        difference_mask = ImageChops(self.previous_image, self.image)
        return difference_mask.getbbox(), self.image.crop(bounding_box)


    def capture_x11_frame(self):
        with mss.mss() as screen:
            monitor = screen.monitors[1]
            image_bytes = screen.grab(monitor)
            self.image = Image.frombytes('RGB', image_bytes.size, image_bytes.bgra, 'raw', 'BGRX')


    def process_image(self):
        bg_image = Image.new('1', (self.epd.width, self.epd.height), 255) 
        if self.image.size[0] != self.epd.width or self.image.size[1] != self.epd.height:
            self.image.thumbnail((self.epd.width, self.epd.height), Image.Resampling.LANCZOS)
        paste_x = (self.epd.width - self.image.size[0]) // 2
        paste_y = (self.epd.height - self.image.size[1]) // 2
        self.image = self.image.convert('L')
        self.image = self.image.filter(ImageFilter.UnsharpMask(radius=150, percent=1500, threshold=3))
        self.image = self.image.convert('1') # Floyd-Steinberg dithering
        bg_image.paste(self.image, (paste_x, paste_y))
        self.image = bg_image

    
    def similarity(self):
        difference_map = ImageChops.difference(self.previous_image, self.image)
        return 1.0 - (numpy.mean(numpy.asarray(difference_map)) / 255.0)

    # deprecated
    def phash_similarity(self):
        hash1 = imagehash.phash(self.previous_image)
        hash2 = imagehash.phash(self.image)
        hamming_distance = hash1 - hash2
        max_bits = len(hash1.hash) ** 2
        return 1.0 - (hamming_distance / max_bits)


if __name__ == '__main__':
    epdx = EPDX()
    epdx.spin()


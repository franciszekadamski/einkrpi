#!/usr/bin/python

import copy
import sys
import os
import logging
import time
from PIL import Image
import imagehash
import mss
import traceback

import epd7in5_V2


class EPDX:
    def __init__(self, display_name: str = ':0'):
        self.epd = epd7in5_V2.EPD()
        self.epd.init()
        self.epd.Clear()
        self.display_name = display_name

        self.similarity_threshold = 0.95

        os.environ['DISPLAY'] = self.display_name
        if 'XAUTHORITY' not in os.environ:
            os.environ['XAUTHORITY'] = f'{os.environ["HOME"]}/.Xauthority' 

        # self.capture_x11_frame()
        # self.process_image()

        # self.previous_image = self.image


    def spin(self):
        while True:
            self.capture() 
            time.sleep(5)


    def capture(self):
        self.capture_x11_frame()
        self.process_image()
        self.previous_image = self.image

        if self.is_new_image_different():
            self.epd.init()
            self.epd.display(self.epd.getbuffer(self.image))
            self.epd.sleep()


    def capture_x11_frame(self):
        with mss.mss() as screen:
            monitor = screen.monitors[1]
            image_bytes = screen.grab(monitor)
            self.image = Image.frombytes('RGB', image_bytes.size, image_bytes.bgra, 'raw', 'BGRX')


    def process_image(self):
        bg_image = Image.new('1', (self.epd.width, self.epd.height), 255) 
        self.image.thumbnail((self.epd.width, self.epd.height), Image.Resampling.LANCZOS)
        paste_x = (self.epd.width - self.image.size[0]) // 2
        paste_y = (self.epd.height - self.image.size[1]) // 2
        self.image = self.image.convert('1')
        bg_image.paste(self.image, (paste_x, paste_y))
        self.image = bg_image


    def phash_similarity(self):
        hash1 = imagehash.phash(self.previous_image)
        hash2 = imagehash.phash(self.image)
        hamming_distance = hash1 - hash2
        max_bits = len(hash1.hash) ** 2
        return 1.0 - (hamming_distance / max_bits)


    def is_new_image_different(self):
        return self.phash_similarity() > self.similarity_threshold



if __name__ == '__main__':
    epdx = EPDX()
    epdx.spin()


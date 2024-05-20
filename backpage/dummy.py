#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import requests
from lxml import html
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)

class Dummy():

    def __init__(self, w = 300, h = 400, image_path = ''):
        logger.debug('Dummy backpage init')
        self.__name = 'dummy'
        p = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
        self.fonts_path = os.path.join(p, 'fonts')
        self.w = w
        self.h = h
        self.image_path = image_path

    @property
    def name(self):
        return self.__name

    def get(self):
        text = "Dummy text"
        return (text)

    def draw(self):
        try:
            text = self.get()
        except SystemError as error:
            raise
            logger.error(error)
            return

        page = Image.new('RGB', (self.w, self.h), "white")
        draw = ImageDraw.Draw(page)

        draw.rectangle((5, 5, self.w-5, self.h-5), outline = 'black', fill='white')

        text_font_size = 30
        text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), text_font_size)
        text_w, text_h = draw.textsize(text, font=text_font)
        while text_w > self.w :
            text_font_size -=2
            text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cousine-Regular.ttf'), text_font_size)
            text_w, text_h = draw.textsize(text, font=text_font)

        draw.text(((self.w-text_w)/2, (self.h-text_h)/2), text, font=text_font, fill='black')

        page.save(os.path.join(self.image_path, 'backsheet.png'))
        logger.info('Back page image saved to file.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    dummy = Dummy()
    dummy.draw()
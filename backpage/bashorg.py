#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import requests
from lxml import etree
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)

class BashOrg():

    def __init__(self, image_path = ''):
        self.__name = 'bashorg.org'
        p = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
        self.fonts_path = os.path.join(p, 'fonts')
        self.image_path = image_path
        self.session = requests.session()

    @property
    def name(self):
        return self.__name

    def get(self):
        attempt = 0
        while True:
            if attempt > 15:
                raise SystemError('Not found fitting item') 
            response = self.session.get('http://bashorg.org/casual')

            tree = etree.HTML(response.content)

            url = tree.xpath('//*[@id="quotes"]/div[@class="q"]/div[@class="vote"]/a[4]/@href')[0]
            title = tree.xpath('//*[@id="quotes"]/div[@class="q"]/div[@class="vote"]/a[4]/text()')[0]
            date = tree.xpath('//*[@id="quotes"]/div[@class="q"]/div[@class="vote"]/text()')[6]
            rank = int(tree.xpath('//*[@id="quotes"]/div[@class="q"]/div[@class="vote"]/span[1]/text()')[0])
            quote_lines = tree.xpath('//*[@id="quotes"]/div[@class="q"]/div[2]/text()')

            chars = sum([len(line) for line in quote_lines])

            if rank > 50 and chars < 400:
                break
            attempt += 1
        logger.info('Item for back page found')
        return (title, date, quote_lines)

    def draw(self):
        try:
            title, date, quote_lines = self.get()
        except SystemError as error:
            raise
            logger.error(error)
            return

        width = 30

        quote = [' '.join([title, date])]
        for line in quote_lines:
            quote += textwrap.wrap(line, width = width)

        quote = '\n'.join(quote)

        page_w = 300
        page_h = 400

        page = Image.new('1', (page_w, page_h), "white")
        draw = ImageDraw.Draw(page)

        font_size = 24
        font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cousine-Regular.ttf'), font_size)
        quote_w, quote_h = draw.textsize(quote, font=font)

        while quote_w > 290 or quote_h > 390:
            logger.debug('wrapped text doesn\'t fit {} {}'.format(quote_w, quote_h))
            logger.debug('font size {}'.format(font_size))
            font_size -=2
            font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cousine-Regular.ttf'), font_size)
            quote_w, quote_h = draw.textsize(quote, font=font)

        logger.debug('now wrapped text fits {} {}'.format(quote_w, quote_h))
        logger.debug('font size {}'.format(font_size))
        draw.text(((page_w-quote_w)/2, (page_h-quote_h)/2), quote, font=font, fill='black')

        page.save(os.path.join(self.image_path, 'backsheet.png'))
        logger.info('Back page image saved to file.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bashorg = BashOrg(os.path.dirname(os.path.realpath(__file__)))
    bashorg.draw()
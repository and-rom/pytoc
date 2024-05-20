#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import requests
from lxml import html
from PIL import Image, ImageDraw, ImageFont
import textwrap

logger = logging.getLogger(__name__)

class XKCD():

    def __init__(self, w = 300, h = 400, image_path = ''):
        logger.debug('XKCD backpage init')
        self.__name = 'xkcd.ru'
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
            if attempt > 5:
                raise SystemError('Not found fitting item')
            response = self.session.get('https://xkcd.ru/random/')

            tree = html.fromstring(response.content)

            url = tree.xpath('/html/body/div/a/img/@src')[0]
            title = tree.xpath('/html/body/div/h1')[0].text_content()
            text = tree.xpath('/html/body/div/div[@class="comics_text"]')[0].text_content().replace('‐','-')

            response = self.session.get(url, stream=True)
            response.raw.decode_content = True
            image=Image.open(response.raw)
            image_w, image_h = image.size
            aspect_ratio = image_w / image_h

            if 0.5 < aspect_ratio and aspect_ratio < 1.5 and max(image_w, image_h) < 600:
                break
            else:
                logger.debug('doesn\'t fit')
            attempt += 1
        logger.info('Item for back page found')
        return (title, image, text)

    def draw(self):
        try:
            title, image, text = self.get()
        except SystemError as error:
            raise
            logger.error(error)
            return

        image.thumbnail((290,300), Image.Resampling.BILINEAR)
        image_w, image_h = image.size

        page_w = 300
        page_h = 400

        page = Image.new('RGBA', (page_w, page_h), "white")
        draw = ImageDraw.Draw(page)

        #draw.rectangle((5, 50, 295, 350), outline = 'black', fill='white')

        title_font_size = 30
        title_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), title_font_size)
        title_w, title_h = draw.textsize(title, font=title_font)
        while title_w > 290 :
            title_font_size -=2
            title_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cousine-Regular.ttf'), title_font_size)
            title_w, title_h = draw.textsize(title, font=title_font)

        draw.text(((page_w-title_w)/2, 10), title, font=title_font, fill='black')

        text_font_size = 24
        text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), text_font_size)
        text_w, text_h = draw.textsize(text, font=text_font)
        if text_w > 290 or text_h > 45:
            logger.debug('text doesn\'t fit {} {}'.format(text_w, text_h))

            texts, text_font_sizes = [], []
            for lines in range(2, 5):
                logger.debug('lines {}'.format(lines))
                col = len(text)//lines
                text_arr = textwrap.wrap(text, width=col)
                while len(text_arr) > lines:
                    logger.debug('wrapping...')
                    col += 2
                    text_arr = textwrap.wrap(text, width=col)

                _text = '\n'.join(text_arr)

                _text_font_size = text_font_size
                text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), text_font_size)
                text_w, text_h = draw.textsize(_text, font=text_font)
                while text_w > 290 or text_h > 45:
                    logger.debug('wrapped text doesn\'t fit {} {}'.format(text_w, text_h))
                    logger.debug('font size {}'.format(_text_font_size))
                    _text_font_size -=2
                    text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), _text_font_size)
                    text_w, text_h = draw.textsize(_text, font=text_font)

                logger.debug('now wrapped text fits {} {}'.format(text_w, text_h))
                logger.debug('font size {}'.format(_text_font_size))
                texts.append(_text)
                text_font_sizes.append(_text_font_size)

            idx_max = max(range(len(text_font_sizes)), key=text_font_sizes.__getitem__)
            text_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), text_font_sizes[idx_max])
            text_w, text_h = draw.textsize(texts[idx_max], font=text_font)
            draw.text(((page_w-text_w)/2, 350), texts[idx_max], font=text_font, fill='black', align='center')
        else:
            draw.text(((page_w-text_w)/2, 350), text, font=text_font, fill='black', align='center')

        page.paste(image, (int((page_w - image_w)/2), int((page_h - image_h)/2)))

        page.save(os.path.join(self.image_path, 'backsheet.png'))
        logger.info('Back page image saved to file.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    xkcd = XKCD()
    xkcd.draw()
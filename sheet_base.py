#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from string import Template
from PIL import Image
import time
screen = True
try:
    from waveshare_epd import epd4in2bc, epd4in2
except ImportError:
    screen = False

logger = logging.getLogger(__name__)

class DeltaTemplate(Template):
    delimiter = "%"

class TearOffCalendarBaseSheet:
    MONTHS = ['январь','февраль','март','апрель','май','июнь','июль','август','сентябрь','октябрь','ноябрь','декабрь']
    WEEKDAYS = ['воскресенье','понедельник','вторник','среда','четверг','пятница','суббота']
    CONSTELLATIONS = {
        'Ari': 'Овен',
        'Tau': 'Телец',
        'Gem': 'Близнецы',
        'Cnc': 'Рак',
        'Leo': 'Лев',
        'Vir': 'Дева',
        'Lib': 'Весы',
        'Sco': 'Скорпион',
        'Sgr': 'Стрелец',
        'Cap': 'Козерог',
        'Aqr': 'Водолей',
        'Psc': 'Рыбы',
        'Aur': 'Возничий',
        'Oph': 'Змееносец',
        'Cet': 'Кит',
        'Ori': 'Орион',
        'Sex': 'Секстант'}
    MOON_PHASES = [
        ['0', 'Ново-\nлуние'],
        ['D', 'Молод.\nлуна'],
        ['G', 'Первая\nчетв.'],
        ['J', 'Растущая\nлуна'],
        ['@', 'Полно-\nлуние'],
        ['Q', 'Убыв.\nлуна'],
        ['T', 'Послед.\nчетв.'],
        ['W', 'Старая\nлуна']]
    DAY_PARTS = {
        'n': 'Ночь',
        'm': 'Утро',
        'd': 'День',
        'e': 'Вечер'}
    BLACK = 0
    RED = 1

    @staticmethod
    def strfdelta(tdelta, fmt):
        d = {"D": tdelta.days}
        d["H"], rem = divmod(tdelta.seconds, 3600)
        d["M"], d["S"] = divmod(rem, 60)
        t = DeltaTemplate(fmt)
        return t.substitute(**d)

    def __init__(self, image_path = ''):
        self.__backpage_name = ''
        p = os.path.dirname(os.path.realpath(__file__))
        self.clip_path = os.path.join(p, 'clip')
        self.fonts_path = os.path.join(p, 'fonts')
        self.icons_path = os.path.join(p, 'icons')
        self.image_path = image_path

        if screen:
            self.epd = epd4in2bc.EPD()
            self.epd_b = epd4in2.EPD()
            self.page_w = self.epd.height
            self.page_h = self.epd.width
        else:
            if self.image_path == '':
                logger.error('There is no screen to draw on and image path not specified')
                return
            self.page_w = 300
            self.page_h = 400

    @property
    def backpage_name(self):
        return self.__backpage_name

    @backpage_name.setter
    def backpage_name(self, s):
        if s != '':
            self.__backpage_name = s
        else:
            raise ValueError

    def display_front(self):
        if screen:
            try:
                pageBlack = Image.open(os.path.join(self.image_path, 'sheet_b.png'))
                pageRed = Image.open(os.path.join(self.image_path, 'sheet_r.png'))

                self.epd.init()
                logger.debug('EPD Init done')
                self.epd.Clear()
                logger.debug('EPD Clear done')

                logger.debug('EPD Display')
                self.epd.display(self.epd.getbuffer(pageBlack), self.epd.getbuffer(pageRed))

                logger.debug('Sleep')
                time.sleep(1)
                logger.debug('EPD Sleep')
                self.epd.sleep()
            except IOError as e:
                print(e)
            else:
                logger.info('EPD rendering completed successfully')
        else:
            logger.info('There is no EPD. You may open saved image from file.')

    def display_back(self):
        if screen:
            try:
                page = Image.open(os.path.join(self.image_path, 'backsheet.png'))

                self.epd_b.Init_4Gray()
                logger.debug('EPD Init done')
                self.epd_b.Clear()
                logger.debug('EPD Clear done')

                logger.debug('EPD Display')
                self.epd_b.display_4Gray(self.epd_b.getbuffer_4Gray(page))

                logger.debug('Sleep')
                time.sleep(1)
                logger.debug('EPD Sleep')
                self.epd.sleep()
            except IOError as e:
                print(e)
            else:
                logger.info('EPD rendering completed successfully')
        else:
            logger.info('There is no EPD. You may open saved image from file.')
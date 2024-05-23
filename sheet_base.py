#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from string import Template
from PIL import Image, ImageFont
import textwrap
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

    def draw_decor_corners(self, page, margin):
        '''
            Draw corners
        '''

        corner = Image.open(os.path.join(self.clip_path, 'corner.png'), mode='r')
        page.paste(corner, (margin, margin), corner)

        corner = corner.rotate(270)
        page.paste(corner, (self.page_w - corner.width - margin, margin), corner)

        corner = corner.rotate(180)
        page.paste(corner, (margin, self.page_h - corner.height - margin), corner)

        corner = corner.rotate(90)
        page.paste(corner, (self.page_w - corner.width - margin, self.page_h - corner.height - margin), corner)

    def draw_decor_three_hlines(self, draw, y, margin, inner_margins, thickness):
        '''
            Draw lines
        '''

        draw.line((margin, y - inner_margins[0], self.page_w - margin, y - inner_margins[0]), fill = 0, width = thickness[0])
        draw.line((margin, y - inner_margins[1], self.page_w - margin, y - inner_margins[1]), fill = 0, width = thickness[1])
        draw.line((margin, y - inner_margins[2], self.page_w - margin, y - inner_margins[2]), fill = 0, width = thickness[2])

    def draw_wifi(self, page, wifi_qlt, x, y):
        wifi = Image.open(os.path.join(self.icons_path, 'wifi', 'wifi_' + str(wifi_qlt) + '.png'), mode='r')
        page.paste(wifi, (x, y), wifi)

    def draw_battery(self, page, battery, battery_charging, x, y):
        battery = Image.open(os.path.join(self.icons_path, 'battery', 'battery_' +  ('charging_' if battery_charging == 1 else '') + str(battery) + '.png'), mode='r')
        if str(x).startswith('r-'):
            x = self.page_w - battery.width - int(x.split('-')[1])
        page.paste(battery, (x, y), battery)

    def draw_day(self, draw, day, y, fontname, fontsize):
        '''
            Draw day
        '''

        day = str(day)

        day_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        day_w, day_h = draw.textsize(day, font=day_font)
        draw.text(((self.page_w-day_w)/2, y), day, font=day_font)

    def draw_month(self, draw, month, x, y, fontname, fontsize):
        '''
            Draw month
        '''

        month = self.MONTHS[month-1].upper()

        month_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        month_w, month_h = draw.textsize(month, font=month_font)
        if str(x).startswith('c'):
            x = (self.page_w-month_w) / 2
        draw.text((x, y), month, font=month_font)

    def draw_weekday(self, draw, weekday, x, y, fontname, fontsize):
        '''
            Draw weekday
        '''

        weekday = self.WEEKDAYS[weekday].upper()

        weekday_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        weekday_w, weekday_h = draw.textsize(weekday, font=weekday_font)
        if str(x).startswith('c'):
            x = (self.page_w - weekday_w) / 2
        elif str(x).startswith('r-'):
            x = self.page_w - weekday_w - int(x.split('-')[1])
        draw.text((x, y), weekday, font=weekday_font)

    def draw_holiday_title(self, draw, holiday_title, holiday_type, y, fontname, fontsize):
        '''
            Draw holiday title
        '''

        if holiday_type in ['int', 'un']:
            holiday_title = '\U0001F310 ' + holiday_title
        elif holiday_type in ['prof']:
            holiday_title = '\U00002692 ' + holiday_title
        else:
            holiday_title = holiday_title
        col = 25
        holiday_title_arr = textwrap.wrap(holiday_title, width=col)
        while len(holiday_title_arr) > 2:
            col += 5
            holiday_title_arr = textwrap.wrap(holiday_title, width=col)
        holiday_title = '\n'.join(holiday_title_arr)
        holiday_font_size = fontsize
        holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), holiday_font_size)
        holiday_w, holiday_h = draw.textsize(holiday_title, font=holiday_font)
        while self.page_w - holiday_w < 80 or holiday_h > 45:
            holiday_font_size -=2
            holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), holiday_font_size)
            holiday_w, holiday_h = draw.textsize(holiday_title, font=holiday_font)
        draw.text(((self.page_w-holiday_w)/2, y-holiday_h/2), holiday_title, font=holiday_font, align='center')


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
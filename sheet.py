#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from data import TearOffCalendarData
from string import Template
import textwrap
from PIL import Image, ImageDraw, ImageFont
import time
screen = True
try:
    from waveshare_epd import epd4in2bc, epd4in2
except ImportError:
    screen = False

logger = logging.getLogger(__name__)

class DeltaTemplate(Template):
    delimiter = "%"

class TearOffCalendarSheet:
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

    @staticmethod
    def __strfdelta(tdelta, fmt):
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

    def draw(self):
        cal = TearOffCalendarData()
        cal_data = cal.get_data()

        pageBlack = Image.new('1', (self.page_w, self.page_h), 255)
        pageRed = Image.new('1', (self.page_w, self.page_h), 255)

        draw = (ImageDraw.Draw(pageBlack), ImageDraw.Draw(pageRed))

        '''
            Draw corners
        '''

        corner = Image.open(os.path.join(self.clip_path, 'corner.png'), mode='r')
        pageBlack.paste(corner, (20, 20), corner)

        corner = corner.rotate(270)
        pageBlack.paste(corner, (230, 20), corner)

        corner = corner.rotate(180)
        pageBlack.paste(corner, (20, 330), corner)

        corner = corner.rotate(90)
        pageBlack.paste(corner, (230, 330), corner)

        # Where to draw parts that may be red.
        i = 0 if not cal_data['dayoff'] or not screen else 1
        logger.debug('Red goes on black for day: ' + 'yes' if i == 0 else 'no')


        '''
            Draw day
        '''

        day = str(cal_data['day'])
        #print(day)

        #draw[0].rectangle((80, 120, 220, 210), outline = 0)
        day_font = ImageFont.truetype(os.path.join(self.fonts_path, 'AbrilFatface-Regular.ttf'), 125)
        day_w, day_h = draw[i].textsize(day, font=day_font)
        draw[i].text(((self.page_w-day_w)/2, 77), day, font=day_font)

        '''
            Draw month
        '''

        month = self.MONTHS[cal_data['month']-1].upper()
        #print(month)

        #draw[0].rectangle((60, 85, 240, 110), outline = 0)
        month_font = ImageFont.truetype(os.path.join(self.fonts_path, 'PlayfairDisplay-ExtraBold.ttf'), 32)
        month_w, month_h = draw[0].textsize(month, font=month_font)
        draw[0].text(((self.page_w-month_w)/2, 75), month, font=month_font)

        '''
            Draw weekday
        '''

        weekday = self.WEEKDAYS[cal_data['weekday']].upper()
        #print(weekday)

        #draw[0].rectangle((60, 220, 240, 245), outline = 0)
        weekday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'PlayfairDisplay-Bold.ttf'), 22)
        weekday_w, weekday_h = draw[i].textsize(weekday, font=weekday_font)
        draw[i].text(((self.page_w-weekday_w)/2, 217), weekday, font=weekday_font)

        '''
            Draw holiday title
        '''

        #draw[0].rectangle((38, 35, 262, 80), outline = 0)

        if cal_data['holiday']:
            if cal_data['holiday_type'] in ['int', 'un']:
                holiday_title = '\U0001F310 ' + cal_data['holiday_title']
            j = 0 if not cal_data['holiday_dayoff'] or not screen else 1
            logger.debug('Red goes on black for holiday: ' + 'yes' if j == 0 else 'no')
            col = 25
            holiday_title_arr = textwrap.wrap(cal_data['holiday_title'], width=col)
            while len(holiday_title_arr) > 2:
                col += 5
                holiday_title_arr = textwrap.wrap(holiday_title, width=col)
            holiday_title = '\n'.join(holiday_title_arr)
            holiday_font_size = 22
            holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Bold.ttf'), holiday_font_size)
            holiday_w, holiday_h = draw[j].textsize(holiday_title, font=holiday_font)
            while self.page_w - holiday_w < 80 or holiday_h > 45:
                holiday_font_size -=2
                holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Bold.ttf'), holiday_font_size)
                holiday_w, holiday_h = draw[j].textsize(holiday_title, font=holiday_font)
            draw[j].text(((self.page_w-holiday_w)/2, 57-holiday_h/2), holiday_title, font=holiday_font, align='center')


        '''
            Draw sun and moon info
        '''

        #draw[0].line((10, 89, 290, 89), fill = 0)

        #draw[0].rectangle((9, 89, 26, 106), outline = 0)
        #draw[0].ellipse((10, 90, 25, 105), fill = 'white', outline='black')
        #draw[0].ellipse((15, 95, 20, 100), fill = 'black')

        sun_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 22)
        draw[0].text((9, 86), '\U00002609', font=sun_font, fill='black')

        #draw[0].rectangle((274, 89, 291, 106), outline = 0)
        #draw[0].ellipse((275, 90, 290, 105), fill = 'black')
        #draw[0].ellipse((271, 90, 286, 105), fill = 'white')

        moon_font = ImageFont.truetype(os.path.join(self.fonts_path, 'moon_phases.ttf'), 18)
        draw[0].text((274, 89), self.MOON_PHASES[cal_data['moon_phase_id']][0], font=moon_font, fill='black')

        s = 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}'.format(
            cal_data['sunrise'].strftime('%H:%M'),
            cal_data['sunset'].strftime('%H:%M'),
            self.__strfdelta(cal_data['daylength'], '%H:%M'))
        #print(s)

        m = 'Заход\n{}\nВосход\n{}\n{}\n{}-й\nдень'.format(
            cal_data['moonset'].strftime('%H:%M'),
            cal_data['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[cal_data['moon_phase_id']][1],
            cal_data['moon_day'])
        #print(m)

        sm_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 16)
        draw[0].text((10, 110), s, font=sm_font, fill='black')
        m_w, m_h = draw[0].textsize(m, font=sm_font)
        draw[0].text((self.page_w-10-m_w, 110), m, font=sm_font, align='right')

        c = 'Луна в созвездии {}'.format(self.CONSTELLATIONS[cal_data['constellation']])
        #print(c)

        #draw[0].rectangle((...), outline = 0)
        c_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Italic.ttf'), 16)
        c_w, c_h = draw[0].textsize(c, font=c_font)
        draw[0].text(((self.page_w-c_w)/2, 245), c, font=c_font)

        '''
            Draw weather forecast
        '''

        y = 270
        #draw[0].rectangle((38, y, 262, y+83), outline = 0)

        #draw[0].line((94, y, 94, y+83), fill = 0)
        #draw[0].line((150, y, 150, y+83), fill = 0)
        #draw[0].line((206, y, 206, y+83), fill = 0)

        #draw[0].line((38, y+20, 262, y+20), fill = 0)
        #draw[0].line((38, y+63, 262, y+63), fill = 0)
        if cal_data['forecast']:
            forecast_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 18)
            pos = 0
            for part in cal_data['forecast']['order']:
                day_part = self.DAY_PARTS[part]
                day_part_w, day_part_h = draw[0].textsize(day_part, font=forecast_font)
                draw[0].text((66-day_part_w/2+pos, y-1), day_part, font=forecast_font, fill='black')
                temp = cal_data['forecast']['parts'][part]['temp']
                temp_w, temp_h = draw[0].textsize(temp, font=forecast_font)
                draw[0].text((66-temp_w/2+pos, y+63), temp, font=forecast_font, fill='black')

                icon = Image.open(os.path.join(self.icons_path, cal_data['forecast']['parts'][part]['icon']+'.png'), mode='r')
                pageBlack.paste(icon, (46+pos, y+22), icon)

                pos += 56
        else:
            no_conn = Image.open(os.path.join(self.clip_path, 'no_connection.png'), mode='r')
            pageBlack.paste(no_conn, (int((self.page_w-no_conn.size[0])/2), y+1), no_conn)

        '''
            Draw back page source name
        '''

        if self.__backpage_name != '':
            backpage_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 12)
            backpage_name_w, backpage_name_h = draw[0].textsize(self.__backpage_name, font=backpage_name_font)
            draw[0].text(((self.page_w-backpage_name_w)/2, 375), self.__backpage_name, font=backpage_name_font)

        '''
            Send images to screen or save to file
        '''
        if screen:
            pageBlack.save(os.path.join(self.image_path, 'sheet_b.png'))
            pageRed.save(os.path.join(self.image_path, 'sheet_r.png'))
            logger.info('Images for EPD saved to files.')
        else:
            pageBlack.save(os.path.join(self.image_path, 'sheet.png'))
            logger.info('There is no EPD. Image saved to file.')

    def display_front(self):
        if screen:
            try:
                pageBlack = Image.open(os.path.join(self.image_path, 'sheet_b.png'))
                pageRed = Image.open(os.path.join(self.image_path, 'sheet_r.png'))

                self.epd.init()
                self.epd.Clear()

                self.epd.display(self.epd.getbuffer(pageBlack), self.epd.getbuffer(pageRed))

                time.sleep(2)
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
                self.epd_b.Clear()

                self.epd_b.display_4Gray(self.epd_b.getbuffer_4Gray(page))

                time.sleep(2)
                self.epd.sleep()
            except IOError as e:
                print(e)
            else:
                logger.info('EPD rendering completed successfully')
        else:
            logger.info('There is no EPD. You may open saved image from file.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    sheet = TearOffCalendarSheet(os.path.dirname(os.path.realpath(__file__)))
    sheet.draw()
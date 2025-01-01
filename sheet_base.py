#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from string import Template
from PIL import Image, ImageDraw, ImageFont
import textwrap
import time

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

        self.screen = True
        if hasattr(self, 'hw_screen') and len(self.hw_screen) == 2:
            try:
                self.epd = getattr(__import__('waveshare_epd', fromlist=self.hw_screen[0:1]), ''.join(self.hw_screen[0:1])).EPD()
                self.epd_b = getattr(__import__('waveshare_epd', fromlist=self.hw_screen[1:2]), ''.join(self.hw_screen[1:2])).EPD()
            except ImportError:
                self.screen = False
                logger.debug('There is no HW screen to draw on. Image will be saved to ' + self.image_path)
        else:
            self.screen = False

        if self.screen:
            self.page_w = self.epd.height
            self.page_h = self.epd.width
        else:
            if self.image_path == '':
                logger.error('There is no HW screen to draw on and image path not specified')
                return
            if not (hasattr(self, 'page_w') or hasattr(self, 'page_h')):
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

    def adjust_fontsize_by_width(self, draw, width, fontname, fontsize, text):
        while True:
            font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
            text_w, text_h = draw.textsize(text, font=font)
            if text_w > width:
                fontsize -= 1
            else:
                break
        return fontsize

    def draw(self, cal_data = None):
        if cal_data is None:
            from data import TearOffCalendarData
            cal = TearOffCalendarData()
            self.cal_data = cal.get_data()
        else:
            self.cal_data = cal_data

        self.pages = (
                    Image.new('1', (self.page_w, self.page_h), 255),
                    Image.new('1', (self.page_w, self.page_h), 255)
                )
        self.draw = (
                    ImageDraw.Draw(self.pages[self.BLACK]),
                    ImageDraw.Draw(self.pages[self.RED])
                )

        # Where to draw parts that may be red.
        self.i = 0 if not self.cal_data['dayoff'] or not self.screen else 1
        self.j = 0 if not self.cal_data['holiday_dayoff'] or not self.screen else 1
        logger.debug('Red goes on black for day: ' + ('yes' if self.i == 0 else 'no'))

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
        wifi_qlt = str(wifi_qlt) if wifi_qlt else 'off'
        wifi = Image.open(os.path.join(self.icons_path, 'wifi', 'wifi_' + wifi_qlt + '.png'), mode='r')
        page.paste(wifi, (x, y), wifi)

    def draw_battery(self, page, battery, x, y):
        battery = Image.open(os.path.join(self.icons_path, 'battery', 'battery_' +  ('charging_' if battery['charging'] == 1 else '') + str(battery['level']) + '.png'), mode='r')
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

    def draw_holiday_title(self, draw, holiday_title, holiday_type, y, margin, max_height, fontname, fontsize, frame = False):
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
        holiday_fontsize = fontsize
        holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), holiday_fontsize)
        holiday_w, holiday_h = draw.textsize(holiday_title, font=holiday_font)
        while self.page_w - holiday_w < margin*2 or holiday_h > max_height:
            holiday_fontsize -=2
            holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), holiday_fontsize)
            holiday_w, holiday_h = draw.textsize(holiday_title, font=holiday_font)
        draw.text(((self.page_w-holiday_w)/2, y-holiday_h/2), holiday_title, font=holiday_font, align='center')

        if frame:
            draw.rectangle((margin, y - holiday_h/2, self.page_w - margin, y + holiday_h/2), outline = 0)

    def draw_sun_info(self, draw, sun_info, sun_info_fmt, icon_x, icon_y, icon_fontname, icon_fontsize, x, y, fontname, fontsize):
        '''
            Draw sun info
        '''

        icon_font = ImageFont.truetype(os.path.join(self.fonts_path, icon_fontname), icon_fontsize)
        draw.text((icon_x, icon_y), '\U00002609', font=icon_font, fill='black')

        sun_info = sun_info_fmt.format(
            sun_info['sunrise'].strftime('%H:%M'),
            sun_info['sunset'].strftime('%H:%M'),
            self.strfdelta(sun_info['daylength'], '%H:%M'))
        sun_info_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        sun_info_w, sun_info_h = draw.textsize(sun_info, font=sun_info_font)
        draw.text((x, y), sun_info, font=sun_info_font, fill='black')

    def draw_moon_info(self, draw, moon_info, moon_info_fmt, icon_x, icon_y, icon_fontname, icon_fontsize, x, y, fontname, fontsize):
        '''
            Draw sun info
        '''

        icon_font = ImageFont.truetype(os.path.join(self.fonts_path, icon_fontname), icon_fontsize)
        draw.text((icon_x, icon_y), self.MOON_PHASES[moon_info['moon_phase_id']][0], font=icon_font, fill='black')

        moon_info = moon_info_fmt.format(
            moon_info['moonset'].strftime('%H:%M'),
            moon_info['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[moon_info['moon_phase_id']][1],
            moon_info['moon_day'])
        moon_info_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        moon_info_w, moon_info_h = draw.textsize(moon_info, font=moon_info_font)
        if str(x).startswith('r-'):
            x = self.page_w - moon_info_w - int(x.split('-')[1])
            align = 'right'
        else:
            align = 'left'
        draw.text((x, y), moon_info, font=moon_info_font, fill='black', align=align)

    def draw_constellation(self, draw, cons, y, fontname, fontsize):
        '''
            Draw constellation
        '''

        cons = 'Луна в созвездии {}'.format(self.CONSTELLATIONS[cons])

        cons_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        cons_w, cons_h = draw.textsize(cons, font=cons_font)
        draw.text(((self.page_w-cons_w)/2, y), cons, font=cons_font)

    def draw_forecast(self, page, draw, forecast, y, margin, part_h, fontname, fontsize, frame = False):
        '''
            Draw weather forecast
        '''

        part_w = int((self.page_w - margin * 2) / 4)
        height = sum(part_h)

        if frame:
            draw.rectangle((margin, y, self.page_w - margin, y + height), outline = 0)

            draw.line((margin + part_w, y, margin + part_w, y + height), fill = 0)
            draw.line((margin + 2 * part_w, y, margin + 2 * part_w, y + height), fill = 0)
            draw.line((margin + 3 * part_w, y, margin + 3 * part_w, y + height), fill = 0)

            draw.line((margin, y + part_h[0], self.page_w - margin, y + part_h[0]), fill = 0)
            draw.line((margin, y + part_h[0] + part_h[1], self.page_w - margin, y + part_h[0] + part_h[1]), fill = 0)

        temp_fontsize = []
        for part in forecast['order']:
            temp_fontsize.append(self.adjust_fontsize_by_width(draw, part_w, fontname, fontsize, forecast['parts'][part]['temp']))
        temp_fontsize = min(temp_fontsize)

        day_part_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        temp_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), temp_fontsize)
        pos = 0
        for part in forecast['order']:
            day_part = self.DAY_PARTS[part]
            day_part_w, day_part_h = draw.textsize(day_part, font=day_part_font)
            draw.text(((part_w/2 + margin)-day_part_w/2+pos, y-1), day_part, font=day_part_font, fill='black')
            temp = forecast['parts'][part]['temp']
            temp_w, temp_h = draw.textsize(temp, font=temp_font)
            draw.text((int((part_w/2 + margin)-temp_w/2+pos), int(y + part_h[0] + part_h[1] + (part_h[2] - temp_h)/2)), temp, font=temp_font, fill='black')

            icon = Image.open(os.path.join(self.icons_path, 'weather', forecast['parts'][part]['icon']+'.png'), mode='r')
            page.paste(icon, (int(margin + (part_w - icon.width) / 2 + pos), int(y + part_h[0] + (part_h[1]-icon.height)/2+0.5)), icon)

            pos += part_w

    def draw_no_conn(self, page, y):
        no_conn = Image.open(os.path.join(self.clip_path, 'no_connection.png'), mode='r')
        page.paste(no_conn, (int((self.page_w-no_conn.size[0])/2), y+1), no_conn)

    def draw_location_name(self, draw, location_name, x, y, fontname, fontsize):
        '''
            Draw location name
        '''

        location_name_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        location_name_w, location_name_h = draw.textsize(location_name, font=location_name_font)
        if str(x).startswith('c'):
            x = (self.page_w - location_name_w) / 2
        elif str(x).startswith('r-'):
            x = self.page_w - location_name_w - int(x.split('-')[1])
        if str(y).startswith('d-'):
            y = self.page_h - location_name_h - int(y.split('-')[1])
        draw.text((x, y), location_name, font=location_name_font)

    def draw_backpage_name(self, draw, backpage_name, x, y, fontname, fontsize):
        '''
            Draw back page source name
        '''

        backpage_name_font = ImageFont.truetype(os.path.join(self.fonts_path, fontname), fontsize)
        backpage_name_w, backpage_name_h = draw.textsize(backpage_name, font=backpage_name_font)
        if str(x).startswith('c'):
            x = (self.page_w - backpage_name_w) / 2
        elif str(x).startswith('r-'):
            x = self.page_w - backpage_name_w - int(x.split('-')[1])
        if str(y).startswith('d-'):
            y = self.page_h - backpage_name_h - int(y.split('-')[1])
        draw.text((x, y), backpage_name, font=backpage_name_font)

    def save(self):
        '''
            Save images
        '''

        if self.screen:
            self.pages[self.BLACK].save(os.path.join(self.image_path, 'sheet_b.png'))
            self.pages[self.RED].save(os.path.join(self.image_path, 'sheet_r.png'))
            logger.info('Images for EPD saved to files.')
        else:
            self.pages[self.BLACK].save(os.path.join(self.image_path, 'sheet.png'))
            logger.info('There is no EPD. Image saved to file.')

    def display_front(self):
        if self.screen:
            try:
                pageBlack = Image.open(os.path.join(self.image_path, 'sheet_b.png'))
                pageRed = Image.open(os.path.join(self.image_path, 'sheet_r.png'))

                logger.info('EPD rendering started')
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
                logger.error('EPD rendering failed with error: ' + e)
            else:
                logger.info('EPD rendering completed successfully')
        else:
            logger.info('There is no EPD. You may open saved image from file.')

    def display_back(self):
        if self.screen:
            try:
                page = Image.open(os.path.join(self.image_path, 'backsheet.png'))

                logger.info('EPD rendering started')
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
                logger.error('EPD rendering failed with error: ' + e)
            else:
                logger.info('EPD rendering completed successfully')
        else:
            logger.info('There is no EPD. You may open saved image from file.')
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sheet_base import TearOffCalendarBaseSheet, DeltaTemplate
import textwrap
from PIL import Image, ImageDraw, ImageFont
screen = True
try:
    from waveshare_epd import epd7in5b_V2
except ImportError:
    screen = False

logger = logging.getLogger(__name__)

class TearOffCalendarSheet(TearOffCalendarBaseSheet):
    def __init__(self, image_path = ''):
        super().__init__(image_path)
        self.clip_path = self.clip_path + '_7in5'
        self.icons_path = self.icons_path + '_7in5'
        if not screen:
            self.page_w = 480
            self.page_h = 800

    def draw(self, cal_data = None):
        if cal_data is None:
            from data import TearOffCalendarData
            cal = TearOffCalendarData()
            cal_data = cal.get_data()

        pageBlack = Image.new('1', (self.page_w, self.page_h), 255)
        pageRed = Image.new('1', (self.page_w, self.page_h), 255)

        pages = (pageBlack, pageRed)
        draw = (ImageDraw.Draw(pageBlack), ImageDraw.Draw(pageRed))

        # Where to draw parts that may be red.
        i = 0 if not cal_data['dayoff'] or not screen else 1
        j = 0 if not cal_data['holiday_dayoff'] or not screen else 1
        logger.debug('Red goes on black for day: ' + 'yes' if i == 0 else 'no')

        wifi = Image.open(os.path.join(self.icons_path, 'wifi', 'wifi_' + str(cal_data['wifi_qlt']) + '.png'), mode='r')
        pages[0].paste(wifi, (2, 3), wifi)

        battery = Image.open(os.path.join(self.icons_path, 'battery', 'battery_' +  ('charging_' if cal_data['battery_charging'] == 1 else '') + str(cal_data['battery']) + '.png'), mode='r')
        pages[0].paste(battery, (self.page_w-34, 3), battery)

        '''
            Draw corners
        '''

        corner = Image.open(os.path.join(self.clip_path, 'corner.png'), mode='r')
        pages[j].paste(corner, (32, 32), corner)

        corner = corner.rotate(270)
        pages[j].paste(corner, (368, 32), corner)

        corner = corner.rotate(180)
        pages[j].paste(corner, (32, 528), corner)

        corner = corner.rotate(90)
        pages[j].paste(corner, (368, 528), corner)

        '''
            Draw day
        '''
        y = 123

        day = str(cal_data['day'])
        #print(day)

        #draw[0].rectangle((128, 192, 352, 336), outline = 0)
        day_font_ttf = 'AbrilFatface-Regular.ttf'
        day_font = ImageFont.truetype(os.path.join(self.fonts_path, day_font_ttf), 200)
        day_w, day_h = draw[i].textsize(day, font=day_font)
        draw[i].text(((self.page_w-day_w)/2, y), day, font=day_font)

        '''
            Draw month
        '''
        y = 120

        month = self.MONTHS[cal_data['month']-1].upper()
        #print(month)

        #draw[0].rectangle((96, 136, 384, 176), outline = 0)
        month_font = ImageFont.truetype(os.path.join(self.fonts_path, 'PlayfairDisplay-ExtraBold.ttf'), 51)
        month_w, month_h = draw[0].textsize(month, font=month_font)
        draw[j].text(((self.page_w-month_w)/2, y), month, font=month_font)

        '''
            Draw weekday
        '''
        y = 347

        weekday = self.WEEKDAYS[cal_data['weekday']].upper()
        #print(weekday)

        #draw[0].rectangle((96, 352, 384, 392), outline = 0)
        weekday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'PlayfairDisplay-Bold.ttf'), 35)
        weekday_w, weekday_h = draw[i].textsize(weekday, font=weekday_font)
        draw[i].text(((self.page_w-weekday_w)/2, y), weekday, font=weekday_font)

        '''
            Draw holiday title
        '''
        y = 91

        #draw[0].rectangle((61, 56, 419, 128), outline = 0)

        if cal_data['holiday']:
            logger.debug('Red goes on black for holiday: ' + 'yes' if j == 0 else 'no')

            if cal_data['holiday_type'] in ['int', 'un']:
                holiday_title = '\U0001F310 ' + cal_data['holiday_title']
            elif cal_data['holiday_type'] in ['prof']:
                holiday_title = '\U00002692 ' + cal_data['holiday_title']
            else:
                holiday_title = cal_data['holiday_title']
            col = 25
            holiday_title_arr = textwrap.wrap(holiday_title, width=col)
            while len(holiday_title_arr) > 2:
                col += 5
                holiday_title_arr = textwrap.wrap(holiday_title, width=col)
            holiday_title = '\n'.join(holiday_title_arr)
            holiday_font_size = 35
            holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Bold.ttf'), holiday_font_size)
            holiday_w, holiday_h = draw[j].textsize(holiday_title, font=holiday_font)
            while self.page_w - holiday_w < 80 or holiday_h > 45:
                holiday_font_size -=2
                holiday_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Bold.ttf'), holiday_font_size)
                holiday_w, holiday_h = draw[j].textsize(holiday_title, font=holiday_font)
            draw[j].text(((self.page_w-holiday_w)/2, y-holiday_h/2), holiday_title, font=holiday_font, align='center')


        '''
            Draw sun and moon info
        '''

        #draw[0].line((16, 143, 464, 143), fill = 0)

        #draw[0].rectangle((15, 143, 42, 169), outline = 0)
        #draw[0].ellipse((16, 144, 40, 168), fill = 'white', outline='black')
        #draw[0].ellipse((24, 152, 32, 160), fill = 'black')

        sun_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 35)
        draw[0].text((15, 138), '\U00002609', font=sun_font, fill='black')

        #draw[0].rectangle((438, 143, 465, 169), outline = 0)
        #draw[0].ellipse((440, 144, 464, 168), fill = 'black')
        #draw[0].ellipse((434, 144, 458, 168), fill = 'white')

        moon_font = ImageFont.truetype(os.path.join(self.fonts_path, 'moon_phases.ttf'), 29)
        draw[0].text((438, 143), self.MOON_PHASES[cal_data['moon_phase_id']][0], font=moon_font, fill='black')

        s = 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}'.format(
            cal_data['sunrise'].strftime('%H:%M'),
            cal_data['sunset'].strftime('%H:%M'),
            self.strfdelta(cal_data['daylength'], '%H:%M'))

        m = 'Заход\n{}\nВосход\n{}\n{}\n{}-й\nдень'.format(
            cal_data['moonset'].strftime('%H:%M'),
            cal_data['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[cal_data['moon_phase_id']][1],
            cal_data['moon_day'])

        sm_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 26)
        draw[0].text((16, 176), s, font=sm_font, fill='black')
        m_w, m_h = draw[0].textsize(m, font=sm_font)
        draw[0].text((self.page_w-16-m_w, 176), m, font=sm_font, align='right')

        '''
            Draw constellation
        '''
        y=392

        #draw[0].rectangle((...), outline = 0)

        c = 'Луна в созвездии {}'.format(self.CONSTELLATIONS[cal_data['constellation']])
        #print(c)

        #draw[0].rectangle((...), outline = 0)
        c_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Italic.ttf'), 26)
        c_w, c_h = draw[0].textsize(c, font=c_font)
        draw[0].text(((self.page_w-c_w)/2, y), c, font=c_font)

        '''
            Draw weather forecast
        '''
        y = 432

        #draw[0].rectangle((61, y, 419, y+133), outline = 0)

        #draw[0].line((150, y, 150, y+133), fill = 0)
        #draw[0].line((240, y, 240, y+133), fill = 0)
        #draw[0].line((330, y, 330, y+133), fill = 0)

        #draw[0].line((61, y+32, 419, y+32), fill = 0)
        #draw[0].line((61, y+101, 419, y+101), fill = 0)

        if cal_data['forecast']:
            forecast_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 29)
            pos = 0
            for part in cal_data['forecast']['order']:
                day_part = self.DAY_PARTS[part]
                day_part_w, day_part_h = draw[0].textsize(day_part, font=forecast_font)
                draw[0].text((106-day_part_w/2+pos, y-1), day_part, font=forecast_font, fill='black')
                temp = cal_data['forecast']['parts'][part]['temp']
                temp_w, temp_h = draw[0].textsize(temp, font=forecast_font)
                draw[0].text((106-temp_w/2+pos, y+101), temp, font=forecast_font, fill='black')

                icon = Image.open(os.path.join(self.icons_path, 'weather', cal_data['forecast']['parts'][part]['icon']+'.png'), mode='r')
                pageBlack.paste(icon, (74+pos, y+35), icon)

                pos += 90
        else:
            no_conn = Image.open(os.path.join(self.clip_path, 'no_connection.png'), mode='r')
            pageBlack.paste(no_conn, (int((self.page_w-no_conn.size[0])/2), y+1), no_conn)

        '''
            Draw location name
        '''

        location_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 19)
        location_name_w, location_name_h = draw[0].textsize(cal_data['location_name'], font=location_name_font)
        draw[0].text(((self.page_w-location_name_w)/2, 24), cal_data['location_name'], font=location_name_font)

        '''
            Draw back page source name
        '''

        if self.backpage_name != '':
            backpage_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 19)
            backpage_name_w, backpage_name_h = draw[0].textsize(self.backpage_name, font=backpage_name_font)
            draw[0].text(((self.page_w-backpage_name_w)/2, 600), self.backpage_name, font=backpage_name_font)

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

if __name__ == "__main__":
    import sys
    import json
    from datetime import datetime, timedelta
    logging.basicConfig(level=logging.DEBUG)
    sheet = TearOffCalendarSheet(os.path.dirname(os.path.realpath(__file__)))
    sheet.backpage_name = 'Back Sheet'
    if len(sys.argv)>1:
        try:
            f = open(sys.argv[1], "r")
        except:
            logger.error("Can't read supplied filename.")
        cal_data = json.loads(f.read())
        cal_data['moonrise'] = datetime.strptime(cal_data['moonrise'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['moonset'] = datetime.strptime(cal_data['moonset'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['sunrise'] = datetime.strptime(cal_data['sunrise'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['sunset'] = datetime.strptime(cal_data['sunset'], '%Y-%m-%d %H:%M:%S.%f')
        t = datetime.strptime(cal_data['daylength'], '%H:%M:%S.%f')
        cal_data['daylength'] = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        sheet.draw(cal_data)
    else:
        sheet.draw()

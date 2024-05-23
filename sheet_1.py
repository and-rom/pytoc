#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sheet_base import TearOffCalendarBaseSheet, DeltaTemplate
import textwrap
from PIL import Image, ImageDraw, ImageFont
screen = True
try:
    from waveshare_epd import epd4in2bc, epd4in2
except ImportError:
    screen = False

logger = logging.getLogger(__name__)

class TearOffCalendarSheet(TearOffCalendarBaseSheet):
    def __init__(self, image_path = ''):
        super().__init__(image_path)

    def draw(self, cal_data = None):
        if cal_data is None:
            from data import TearOffCalendarData
            cal = TearOffCalendarData()
            cal_data = cal.get_data()

        pages = (
                    Image.new('1', (self.page_w, self.page_h), 255),
                    Image.new('1', (self.page_w, self.page_h), 255)
                )
        draw = (
                    ImageDraw.Draw(pages[self.BLACK]),
                    ImageDraw.Draw(pages[self.RED])
                )

        # Where to draw parts that may be red.
        i = self.BLACK if not cal_data['dayoff'] or not screen else self.RED
        j = self.BLACK if not cal_data['holiday_dayoff'] or not screen else self.RED
        logger.debug('Red goes on black for day: ' + 'yes' if i == 0 else 'no')

        wifi = Image.open(os.path.join(self.icons_path, 'wifi', 'wifi_' + str(cal_data['wifi_qlt']) + '.png'), mode='r')
        pages[self.BLACK].paste(wifi, (1, 2), wifi)

        battery = Image.open(os.path.join(self.icons_path, 'battery', 'battery_' +  ('charging_' if cal_data['battery_charging'] == 1 else '') + str(cal_data['battery']) + '.png'), mode='r')
        pages[self.BLACK].paste(battery, (self.page_w-21, 2), battery)

        self.draw_decor_corners(pages[j], 20)

        self.draw_day(draw[i], cal_data['day'], 80, 'AbrilFatface-Regular.ttf', 125)

        self.draw_month(draw[j], cal_data['month'], 'c', 78, 'PlayfairDisplay-ExtraBold.ttf', 32)

        self.draw_weekday(draw[i], cal_data['weekday'], 'c', 220, 'PlayfairDisplay-Bold.ttf', 22)

        if cal_data['holiday']:
            logger.debug('Red goes on black for holiday: ' + 'yes' if j == self.BLACK else 'no')
            self.draw_holiday_title(draw[j], cal_data['holiday_title'], cal_data['holiday_type'], 55, 'Cuprum-Bold.ttf', 22)


        '''
            Draw sun and moon info
        '''

        #draw[0].line((10, 89, 290, 89), fill = 0)

        #draw[0].rectangle((9, 89, 26, 106), outline = 0)
        #draw[0].ellipse((10, 90, 25, 105), fill = 'white', outline='black')
        #draw[0].ellipse((15, 95, 20, 100), fill = 'black')

        sun_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 22)
        draw[self.BLACK].text((9, 86), '\U00002609', font=sun_font, fill='black')

        #draw[0].rectangle((274, 89, 291, 106), outline = 0)
        #draw[0].ellipse((275, 90, 290, 105), fill = 'black')
        #draw[0].ellipse((271, 90, 286, 105), fill = 'white')

        moon_font = ImageFont.truetype(os.path.join(self.fonts_path, 'moon_phases.ttf'), 18)
        draw[self.BLACK].text((274, 89), self.MOON_PHASES[cal_data['moon_phase_id']][0], font=moon_font, fill='black')

        s = 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}'.format(
            cal_data['sunrise'].strftime('%H:%M'),
            cal_data['sunset'].strftime('%H:%M'),
            self.strfdelta(cal_data['daylength'], '%H:%M'))
        #print(s)

        m = 'Заход\n{}\nВосход\n{}\n{}\n{}-й\nдень'.format(
            cal_data['moonset'].strftime('%H:%M'),
            cal_data['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[cal_data['moon_phase_id']][1],
            cal_data['moon_day'])
        #print(m)

        sm_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 16)
        draw[self.BLACK].text((10, 110), s, font=sm_font, fill='black')
        m_w, m_h = draw[self.BLACK].textsize(m, font=sm_font)
        draw[self.BLACK].text((self.page_w-10-m_w, 110), m, font=sm_font, align='right')

        '''
            Draw constellation
        '''
        y=248

        #draw[0].rectangle((...), outline = 0)

        c = 'Луна в созвездии {}'.format(self.CONSTELLATIONS[cal_data['constellation']])
        #print(c)

        #draw[0].rectangle((...), outline = 0)
        c_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Italic.ttf'), 16)
        c_w, c_h = draw[self.BLACK].textsize(c, font=c_font)
        draw[self.BLACK].text(((self.page_w-c_w)/2, y), c, font=c_font)

        '''
            Draw weather forecast
        '''
        y = 272

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
                day_part_w, day_part_h = draw[self.BLACK].textsize(day_part, font=forecast_font)
                draw[self.BLACK].text((66-day_part_w/2+pos, y-1), day_part, font=forecast_font, fill='black')
                temp = cal_data['forecast']['parts'][part]['temp']
                temp_w, temp_h = draw[self.BLACK].textsize(temp, font=forecast_font)
                draw[self.BLACK].text((66-temp_w/2+pos, y+63), temp, font=forecast_font, fill='black')

                icon = Image.open(os.path.join(self.icons_path, 'weather', cal_data['forecast']['parts'][part]['icon']+'.png'), mode='r')
                pages[self.BLACK].paste(icon, (46+pos, y+22), icon)

                pos += 56
        else:
            no_conn = Image.open(os.path.join(self.clip_path, 'no_connection.png'), mode='r')
            pages[self.BLACK].paste(no_conn, (int((self.page_w-no_conn.size[0])/2), y+1), no_conn)

        '''
            Draw location name
        '''
        y = 15

        location_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 12)
        location_name_w, location_name_h = draw[self.BLACK].textsize(cal_data['location_name'], font=location_name_font)
        draw[self.BLACK].text(((self.page_w-location_name_w)/2, y), cal_data['location_name'], font=location_name_font)

        '''
            Draw back page source name
        '''
        y = 13

        if self.backpage_name != '':
            backpage_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 12)
            backpage_name_w, backpage_name_h = draw[self.BLACK].textsize(self.backpage_name, font=backpage_name_font)
            draw[self.BLACK].text(((self.page_w-backpage_name_w)/2, self.page_h-y-backpage_name_h), self.backpage_name, font=backpage_name_font)

        '''
            Send images to screen or save to file
        '''
        if screen:
            pages[self.BLACK].save(os.path.join(self.image_path, 'sheet_b.png'))
            pages[self.RED].save(os.path.join(self.image_path, 'sheet_r.png'))
            logger.info('Images for EPD saved to files.')
        else:
            pages[self.BLACK].save(os.path.join(self.image_path, 'sheet.png'))
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

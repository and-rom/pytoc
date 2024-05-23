#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sheet_base import TearOffCalendarBaseSheet, DeltaTemplate
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
        i = 0 if not cal_data['dayoff'] or not screen else 1
        j = 0 if not cal_data['holiday_dayoff'] or not screen else 1
        logger.debug('Red goes on black for day: ' + 'yes' if i == 0 else 'no')

        self.draw_decor_three_hlines(draw[j], 210, 10, (8, 5, 2), (3, 2, 1))
        self.draw_wifi(pages[self.BLACK], cal_data['wifi_qlt'], 1, 2)
        self.draw_battery(pages[self.BLACK], cal_data['battery'], cal_data['battery_charging'], 'r-1', 2)
        self.draw_day(draw[i], cal_data['day'], 235, 'Molot.otf', 120)
        self.draw_month(draw[j], cal_data['month'], 10, 205, 'ZenAntiqueSoft-Regular.ttf', 20)
        self.draw_weekday(draw[i], cal_data['weekday'], 'r-10', 205, 'ZenAntiqueSoft-Regular.ttf', 20)
        if cal_data['holiday']:
            logger.debug('Red goes on black for holiday: ' + 'yes' if j == 0 else 'no')
            self.draw_holiday_title(draw[j], cal_data['holiday_title'], cal_data['holiday_type'], 153, 'Cuprum-Bold.ttf', 22)

        '''
            Draw sun and moon info
        '''

        y=240
        #draw[0].line((10, 89+170, 290, 89+170), fill = 0)

        #draw[0].rectangle((9, 89+170, 26, 106+170), outline = 0)
        #draw[0].ellipse((10, 90+170, 25, 105+170), fill = 'white', outline='black')
        #draw[0].ellipse((15, 95+170, 20, 100+170), fill = 'black')

        sun_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 22)
        draw[self.BLACK].text((9, y-4), '\U00002609', font=sun_font, fill='black')

        #draw[0].rectangle((274, 89+170, 291, 106+170), outline = 0)
        #draw[0].ellipse((275, 90+170, 290, 105+170), fill = 'black')
        #draw[0].ellipse((271, 90+170, 286, 105+170), fill = 'white')

        moon_font = ImageFont.truetype(os.path.join(self.fonts_path, 'moon_phases.ttf'), 18)
        draw[self.BLACK].text((274, y-1), self.MOON_PHASES[cal_data['moon_phase_id']][0], font=moon_font, fill='black')

        s = 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}'.format(
            cal_data['sunrise'].strftime('%H:%M'),
            cal_data['sunset'].strftime('%H:%M'),
            super().strfdelta(cal_data['daylength'], '%H:%M'))
        #print(s)

        m = 'Заход\n{}\nВосход\n{}\n{}\nд. {}'.format(
            cal_data['moonset'].strftime('%H:%M'),
            cal_data['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[cal_data['moon_phase_id']][1],
            cal_data['moon_day'])
        #print(m)

        sm_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 14)
        draw[self.BLACK].text((10, y+20), s, font=sm_font, fill='black')
        m_w, m_h = draw[self.BLACK].textsize(m, font=sm_font)
        draw[self.BLACK].text((self.page_w-10-m_w, y+20), m, font=sm_font, align='right')

        '''
            Draw constellation
        '''

        y=360
        #draw[0].rectangle((...), outline = 0)

        c = 'Луна в созвездии {}'.format(self.CONSTELLATIONS[cal_data['constellation']])
        #print(c)

        #draw[0].rectangle((...), outline = 0)
        c_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Italic.ttf'), 16)
        c_w, c_h = draw[self.BLACK].textsize(c, font=c_font)
        draw[self.BLACK].text(((self.page_w-c_w)/2, y), c, font=c_font)

        if cal_data['forecast']:
            self.draw_forecast(pages[self.BLACK], draw[self.BLACK], cal_data['forecast'], 15, 38, (20, 43, 20), 'Cuprum-Regular.ttf', 18, (3, 2, 1))
        else:
            self.draw_no_conn(pages[self.BLACK], 15)

        '''
            Draw location name
        '''

        location_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 12)
        location_name_w, location_name_h = draw[self.BLACK].textsize(cal_data['location_name'], font=location_name_font)
        draw[self.BLACK].text((10, self.page_h-location_name_h-2), cal_data['location_name'], font=location_name_font)

        '''
            Draw back page source name
        '''

        if self.backpage_name != '':
            backpage_name_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 12)
            backpage_name_w, backpage_name_h = draw[self.BLACK].textsize(self.backpage_name, font=backpage_name_font)
            draw[self.BLACK].text((self.page_w-backpage_name_w-10, self.page_h-backpage_name_h-2), self.backpage_name, font=backpage_name_font)

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

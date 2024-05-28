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
        i = self.BLACK if not cal_data['dayoff'] or not screen else self.RED
        j = self.BLACK if not cal_data['holiday_dayoff'] or not screen else self.RED
        logger.debug('Red goes on black for day: ' + 'yes' if i == 0 else 'no')

        self.draw_decor_corners(pages[j], 20)
        self.draw_wifi(pages[self.BLACK], cal_data['wifi_qlt'], 1, 2)
        self.draw_battery(pages[self.BLACK], cal_data['battery'], cal_data['battery_charging'], 'r-1', 2)
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
        draw[self.BLACK].text((274, 89), self.MOON_PHASES[cal_data['moon_info']['moon_phase_id']][0], font=moon_font, fill='black')

        s = 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}'.format(
            cal_data['sun_info']['sunrise'].strftime('%H:%M'),
            cal_data['sun_info']['sunset'].strftime('%H:%M'),
            self.strfdelta(cal_data['sun_info']['daylength'], '%H:%M'))
        #print(s)

        m = 'Заход\n{}\nВосход\n{}\n{}\n{}-й\nдень'.format(
            cal_data['moon_info']['moonset'].strftime('%H:%M'),
            cal_data['moon_info']['moonrise'].strftime('%H:%M'),
            self.MOON_PHASES[cal_data['moon_info']['moon_phase_id']][1],
            cal_data['moon_info']['moon_day'])
        #print(m)

        sm_font = ImageFont.truetype(os.path.join(self.fonts_path, 'Cuprum-Regular.ttf'), 16)
        draw[self.BLACK].text((10, 110), s, font=sm_font, fill='black')
        m_w, m_h = draw[self.BLACK].textsize(m, font=sm_font)
        draw[self.BLACK].text((self.page_w-10-m_w, 110), m, font=sm_font, align='right')

        self.draw_constellation(draw[self.BLACK], cal_data['moon_info']['constellation'], 248, 'Cuprum-Italic.ttf', 16)

        if cal_data['forecast']:
            self.draw_forecast(pages[self.BLACK], draw[self.BLACK], cal_data['forecast'], 272, 38, (20, 43, 20), 'Cuprum-Regular.ttf', 18, (3, 2, 1))
        else:
            self.draw_no_conn(pages[self.BLACK], 272)

        self.draw_location_name(draw[self.BLACK], cal_data['location_name'], 'c', 15, 'Cuprum-Regular.ttf', 12)

        if self.backpage_name != '':
            self.draw_backpage_name(draw[self.BLACK], self.backpage_name, 'c', 'd-13', 'Cuprum-Regular.ttf', 12)

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
        cal_data['moon_info']['moonrise'] = datetime.strptime(cal_data['moon_info']['moonrise'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['moon_info']['moonset'] = datetime.strptime(cal_data['moon_info']['moonset'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['sun_info']['sunrise'] = datetime.strptime(cal_data['sun_info']['sunrise'], '%Y-%m-%d %H:%M:%S.%f')
        cal_data['sun_info']['sunset'] = datetime.strptime(cal_data['sun_info']['sunset'], '%Y-%m-%d %H:%M:%S.%f')
        t = datetime.strptime(cal_data['sun_info']['daylength'], '%H:%M:%S.%f')
        cal_data['sun_info']['daylength'] = timedelta(hours=t.hour, minutes=t.minute, seconds=t.second, microseconds=t.microsecond)
        sheet.draw(cal_data)
    else:
        sheet.draw()

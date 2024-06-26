#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sheet_base import TearOffCalendarBaseSheet, DeltaTemplate
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

        if screen:
            self.epd = epd7in5b_V2.EPD()
            self.epd_b = epd7in5b_V2.EPD()
            self.page_w = self.epd.height
            self.page_h = self.epd.width
        else:
            if self.image_path == '':
                logger.error('There is no screen to draw on and image path not specified')
                return
            self.page_w = 480
            self.page_h = 800

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

        self.draw_decor_corners(pages[j], 32)
        self.draw_wifi(pages[self.BLACK], cal_data['wifi_qlt'], 2, 3)
        self.draw_battery(pages[self.BLACK], cal_data['battery'], 'r-2', 3)
        self.draw_day(draw[i], cal_data['day'], 200, 'AbrilFatface-Regular.ttf', 200)
        self.draw_month(draw[j], cal_data['month'], 'c', 150, 'PlayfairDisplay-ExtraBold.ttf', 51)
        self.draw_weekday(draw[i], cal_data['weekday'], 'c', 450, 'PlayfairDisplay-Bold.ttf', 35)
        if cal_data['holiday']:
            logger.debug('Red goes on black for holiday: ' + 'yes' if j == 0 else 'no')
            self.draw_holiday_title(draw[j], cal_data['holiday_title'], cal_data['holiday_type'], 91, 'Cuprum-Bold.ttf', 38)
        self.draw_sun_info(draw[self.BLACK], cal_data['sun_info'], 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}', 15, 182, 'Cuprum-Regular.ttf', 35, 16, 220, 'Cuprum-Regular.ttf', 26)
        self.draw_moon_info(draw[self.BLACK], cal_data['moon_info'], 'Заход\n{}\nВосход\n{}\n{}\n{}-й\nдень', 438, 182, 'moon_phases.ttf', 29, 'r-16', 220, 'Cuprum-Regular.ttf', 26)
        self.draw_constellation(draw[self.BLACK], cal_data['moon_info']['constellation'], 520, 'Cuprum-Italic.ttf', 26)
        if cal_data['forecast']:
            self.draw_forecast(pages[self.BLACK], draw[self.BLACK], cal_data['forecast'], 575, 61, (32, 69, 32), 'Cuprum-Regular.ttf', 29, (5, 3, 1))
        else:
            self.draw_no_conn(pages[self.BLACK], 575)
        self.draw_location_name(draw[self.BLACK], cal_data['location_name'], 'c', 5, 'Cuprum-Regular.ttf', 15)
        if self.backpage_name != '':
            self.draw_backpage_name(draw[self.BLACK], self.backpage_name, 'c', 'd-5', 'Cuprum-Regular.ttf', 15)

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

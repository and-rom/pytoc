#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
from sheet_base import TearOffCalendarBaseSheet, DeltaTemplate

logger = logging.getLogger(__name__)

class TearOffCalendarSheet(TearOffCalendarBaseSheet):
    def __init__(self, image_path = ''):
        self.hw_screen = ['epd7in5b_V2', 'epd7in5b_V2']
        self.page_w = 480
        self.page_h = 800
        super().__init__(image_path)

        self.clip_path = self.clip_path + '_7in5'
        self.icons_path = self.icons_path + '_7in5'

    def draw(self, cal_data = None):
        super().draw(cal_data)

        self.draw_decor_three_hlines(self.draw[self.j], 350, 16, (6, 4, 2), (1, 2))
        self.draw_wifi(self.pages[self.BLACK], self.cal_data['wifi_qlt'], 2, 3)
        self.draw_battery(self.pages[self.BLACK], self.cal_data['battery'], 'r-2', 3)
        self.draw_day(self.draw[self.i], self.cal_data['day'], 485, 'Molot.otf', 200)
        self.draw_month(self.draw[self.j], self.cal_data['month'], 16, 370, 'ZenAntiqueSoft-Regular.ttf', 42)
        self.draw_weekday(self.draw[self.i], self.cal_data['weekday'], 'r-16', 410, 'ZenAntiqueSoft-Regular.ttf', 42)
        if self.cal_data['holiday']:
            logger.debug('Red goes on black for holiday: ' + 'yes' if self.j == 0 else 'no')
            self.draw_holiday_title(self.draw[self.j], self.cal_data['holiday_title'], self.cal_data['holiday_type'], 290, 32, 148, 'Cuprum-Bold.ttf', 48)
        self.draw_sun_info(self.draw[self.BLACK], self.cal_data['sun_info'], 'Восход\n{}\nЗаход\n{}\nДолгота\nдня\n{}', 14, 481, 'Cuprum-Regular.ttf', 38, 16, 516, 'Cuprum-Regular.ttf', 24)
        self.draw_moon_info(self.draw[self.BLACK], self.cal_data['moon_info'], 'Заход\n{}\nВосход\n{}\n{}\nд. {}', 434, 485, 'moon_phases.ttf', 32, 'r-16', 516, 'Cuprum-Regular.ttf', 24)
        self.draw_constellation(self.draw[self.BLACK], self.cal_data['moon_info']['constellation'], 700, 'Cuprum-Italic.ttf', 30)
        if self.cal_data['forecast']:
            self.draw_forecast(self.pages[self.BLACK], self.draw[self.BLACK], self.cal_data['forecast'], 50, 16, (40, 69, 40, 44), 'Cuprum-Regular.ttf', 32)
        else:
            self.draw_no_conn(self.pages[self.BLACK], 24)
        self.draw_location_name(self.draw[self.BLACK], self.cal_data['location_name'], 16, 'd-3', 'Cuprum-Regular.ttf', 22)
        if self.backpage_name != '':
            self.draw_backpage_name(self.draw[self.BLACK], self.backpage_name, 'r-16', 'd-3', 'Cuprum-Regular.ttf', 22)

        self.save()

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

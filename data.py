#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import json
from datetime import datetime
import locale
import ephem
from owm import OWM
from pprint import pprint

logger = logging.getLogger(__name__)

class TearOffCalendarData:

    @staticmethod
    def __get_moon_phase(observer):
        target_date_utc = observer.date
        target_date_local = ephem.localtime( target_date_utc ).date()
        next_full = ephem.localtime( ephem.next_full_moon(target_date_utc) ).date()
        next_new = ephem.localtime( ephem.next_new_moon(target_date_utc) ).date()
        next_last_quarter = ephem.localtime( ephem.next_last_quarter_moon(target_date_utc) ).date()
        next_first_quarter = ephem.localtime( ephem.next_first_quarter_moon(target_date_utc) ).date()
        previous_full = ephem.localtime( ephem.previous_full_moon(target_date_utc) ).date()
        previous_new = ephem.localtime( ephem.previous_new_moon(target_date_utc) ).date()
        previous_last_quarter = ephem.localtime( ephem.previous_last_quarter_moon(target_date_utc) ).date()
        previous_first_quarter = ephem.localtime( ephem.previous_first_quarter_moon(target_date_utc) ).date()

        if target_date_local in (next_full, previous_full):
            return 4
        elif target_date_local in (next_new, previous_new):
            return 0
        elif target_date_local in (next_first_quarter, previous_first_quarter):
            return 2
        elif target_date_local in (next_last_quarter, previous_last_quarter):
            return 6
        elif previous_new < next_first_quarter < next_full < next_last_quarter < next_new:
            return 1
        elif previous_first_quarter < next_full < next_last_quarter < next_new < next_first_quarter:
            return 3
        elif previous_full < next_last_quarter < next_new < next_first_quarter < next_full:
            return 5
        elif previous_last_quarter < next_new < next_first_quarter < next_full < next_last_quarter:
            return 7

    def get_data(self):
        try:
            locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
        except locale.Error:
            pass

        cal_data = {}

        today = datetime.today()
        btoday = today.replace(hour=0, minute=0, second=0, microsecond=0)
        etoday = today.replace(hour=23, minute=59, second=59, microsecond=999)

        cd = int(today.strftime('%-d')), int(today.strftime('%-m'))
        cal_data['day'] = cd[0]
        cal_data['month'] = cd[1]
        cal_data['weekday'] = int(today.strftime('%w'))
        cal_data['dayoff'] = False
        cal_data['holiday'] = False

        with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'misc', 'holidays.json'), 'rb') as f:
            data = json.load(f)
            if cd[0] in data["daysOff"][cd[1]-1]:
                dayoff = True
            if data['holidays'][cd[1]-1][cd[0]-1]['title'] != '':
                cal_data['holiday'] = True
                cal_data['holiday_title'] = data['holidays'][cd[1]-1][cd[0]-1]['title']
                cal_data['holiday_dayoff'] = bool(data['holidays'][cd[1]-1][cd[0]-1]['dayoff'])
                cal_data['holiday_type'] = data['holidays'][cd[1]-1][cd[0]-1]['type']

        coord = '55.583710', '37.590857'
        home = ephem.Observer()
        home.lat, home.lon = coord
        home.date = ephem.now()
        sun = ephem.Sun()
        sun.compute(home)
        srp = ephem.localtime(home.previous_rising(sun))
        srn = ephem.localtime(home.next_rising(sun))
        ssp = ephem.localtime(home.previous_setting(sun))
        ssn = ephem.localtime(home.next_setting(sun))
        cal_data['sunrise'] = srn if srp < btoday else srp
        cal_data['sunset'] = ssn if ssn < etoday else ssp
        cal_data['daylength'] = cal_data['sunset'] - cal_data['sunrise']

        moon = ephem.Moon()
        moon.compute(home)
        mrp = ephem.localtime(home.previous_rising(moon))
        mrn = ephem.localtime(home.next_rising(moon))
        msp = ephem.localtime(home.previous_setting(moon))
        msn = ephem.localtime(home.next_setting(moon))
        cal_data['moonrise'] = mrn if mrp < btoday else mrp
        cal_data['moonset'] = msn if msn < etoday else msp

        cal_data['constellation'] = ephem.constellation(moon)[0]

        cal_data['moon_day'] = int(home.date - ephem.previous_new_moon(home.date))+1
        cal_data['moon_phase_id'] = self.__get_moon_phase(home)

        owm = OWM()
        cal_data['forecast'] = owm.get_forecast(coord)

        return cal_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cal = TearOffCalendarData()
    cal_data = cal.get_data()
    pprint(cal_data)
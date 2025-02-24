#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import logging
import configparser
from datetime import datetime
import locale
import ephem
from owm import OWM
from gm import GM
import wifi
import json

logger = logging.getLogger(__name__)

def map_to_range(value, inMin, inMax, outMin, outMax):
  return outMin + (float(value - inMin) / float(inMax - inMin) * (outMax - outMin))

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

        if os.path.isfile(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini')):
            config = configparser.ConfigParser()
            config.read(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.ini'))
            cal_data['location'] = config['Common']['CurrentLocation']
            cal_data['latitude'] = config[cal_data['location']]['Latitude']
            cal_data['longitude'] = config[cal_data['location']]['Longitude']
            cal_data['location_name'] = config[cal_data['location']]['Name']
            weather_service = config['Common']['WeatherService']
            wifi_device = config['Common']['WiFiDevice']
        else:
            cal_data['location'] = 'Moscow'
            cal_data['latitude'] = 55.755864
            cal_data['longitude'] = 37.617698
            cal_data['location_name'] = 'Москва'
            weather_service = None
            wifi_device = None

        today = datetime.today()
        btoday = today.replace(hour=0, minute=0, second=0, microsecond=0)
        etoday = today.replace(hour=23, minute=59, second=59, microsecond=999)

        t = today
        cd = int(t.strftime('%-d')), int(t.strftime('%-m'))
        cal_data['day'] = cd[0]
        cal_data['month'] = cd[1]
        cal_data['weekday'] = int(t.strftime('%w'))
        cal_data['dayoff'] = False
        cal_data['holiday'] = False
        cal_data['holiday_dayoff'] = False
        year = t.strftime('%Y')

        try:
            with open(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'misc', 'holidays_' + year + '.json'), 'rb') as f:
                data = json.load(f)
                if 'daysOff' in data and cd[0] in data["daysOff"][cd[1]-1]:
                    cal_data['dayoff'] = True
                if 'holidays' in data and data['holidays'][cd[1]-1][cd[0]-1]['title'] != '':
                    cal_data['holiday'] = True
                    cal_data['holiday_title'] = data['holidays'][cd[1]-1][cd[0]-1]['title']
                    cal_data['holiday_dayoff'] = bool(data['holidays'][cd[1]-1][cd[0]-1]['dayoff'])
                    cal_data['holiday_type'] = data['holidays'][cd[1]-1][cd[0]-1]['type']
        except FileNotFoundError:
            pass

        home = ephem.Observer()
        home.lat, home.lon = cal_data['latitude'], cal_data['longitude']
        home.date = ephem.now()
        sun = ephem.Sun()
        sun.compute(home)
        srp = ephem.localtime(home.previous_rising(sun))
        srn = ephem.localtime(home.next_rising(sun))
        ssp = ephem.localtime(home.previous_setting(sun))
        ssn = ephem.localtime(home.next_setting(sun))
        cal_data['sun_info'] = {}
        cal_data['sun_info']['sunrise'] = srn if srp < btoday else srp
        cal_data['sun_info']['sunset'] = ssn if ssn < etoday else ssp
        cal_data['sun_info']['daylength'] = cal_data['sun_info']['sunset'] - cal_data['sun_info']['sunrise']

        moon = ephem.Moon()
        moon.compute(home)
        mrp = ephem.localtime(home.previous_rising(moon))
        mrn = ephem.localtime(home.next_rising(moon))
        msp = ephem.localtime(home.previous_setting(moon))
        msn = ephem.localtime(home.next_setting(moon))
        cal_data['moon_info'] = {}
        cal_data['moon_info']['moonrise'] = mrn if mrp < btoday else mrp
        cal_data['moon_info']['moonset'] = msn if msn < etoday else msp

        cal_data['moon_info']['constellation'] = ephem.constellation(moon)[0]

        cal_data['moon_info']['moon_day'] = int(home.date - ephem.previous_new_moon(home.date))+1
        cal_data['moon_info']['moon_phase_id'] = self.__get_moon_phase(home)

        if weather_service:
            weather = globals()[weather_service]()
            cal_data['forecast'] = weather.get_forecast((cal_data['latitude'], cal_data['longitude']))
        else:
            cal_data['forecast'] = {}

        if wifi_device:
            wifi_qlt = wifi.get_quality('wlan0')
            cal_data['wifi_qlt'] = round(map_to_range(wifi_qlt, 0, 100, 0, 4)) if wifi_qlt else None
        else:
            cal_data['wifi_qlt'] = None

        cal_data['battery'] = {}
        try:
            import ina219
            ups = ina219.INA219(addr=0x43)
            cal_data['battery']['level'] = round(ups.getPercent())//10*10
            cal_data['battery']['charging'] = ups.getCharging()
            if cal_data['battery']['level'] < 20:
                cal_data['battery']['level'] = 20
            elif cal_data['battery']['level'] == 40:
                cal_data['battery']['level'] = 30
            elif cal_data['battery']['level'] == 70:
                cal_data['battery']['level'] = 60
            elif cal_data['battery']['level'] >= 90 and cal_data['battery']['charging'] == 1:
                cal_data['battery']['level'] = 100
        except ImportError:
            cal_data['battery']['level'] = 'unknown'
            cal_data['battery']['charging'] = 0

        logger.info('Calendar data collected')

        return cal_data

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    cal = TearOffCalendarData()
    cal_data = cal.get_data()
    print(json.dumps(cal_data, indent=4, sort_keys=True, default=str, ensure_ascii=False))
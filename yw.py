#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime, timedelta
from yw_cfg import access_key
import json

logger = logging.getLogger(__name__)

class YW:

    @staticmethod
    def __get_daypart(date):
        hour = int(date.strftime('%-H'))
        if 0 <= hour < 6:
            return 'n'
        if 6 <= hour < 12:
            return 'm'
        if 12 <= hour < 18:
            return 'd'
        if 18 <= hour <= 23:
            return 'e'

    @staticmethod
    def __most_common(lst):
        lst=[el for el in lst if el is not None]
        return max(set(lst), key = lst.count) if len(lst) != 0 else None

    @staticmethod
    def __average(lst):
        lst=[el for el in lst if el is not None]
        return sum(lst) / len(lst) if len(lst) != 0 else None

    @staticmethod
    def __add_sign(num):
        if num > 0:
            sign = '+'
        else:
            sign = ''
        return sign+str(num)

    def get_forecast(self, coord):
        headers = {'X-Yandex-Weather-Key': access_key}

        payload = {
            'lat': coord[0],
            'lon': coord[1]
        }


        try:
            response = requests.get('https://api.weather.yandex.ru/v2/forecast', headers=headers, params=payload, timeout=(10,30))
        except Exception as e:
            logger.error('Error getting weather forecast data')
            return {}
        else:
            weather_data = response.json()

            if 'forecasts' not in weather_data or not weather_data['forecasts']:
                logger.error('Error getting weather forecast data')
                logger.debug(weather_data)
                return {}
            else:
                logger.info('Weather forecast data received successfully')

        now = datetime.now()
        hour = int(now.strftime('%-H'))
        not_before = now.replace(hour=hour - hour % 6, minute=0, second=0, microsecond=0)
        not_after = not_before + timedelta(hours=23)

        summary = {
            'order' : [],
            'parts': {
                'n': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'icon':[]},
                'm': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'icon':[]},
                'd': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'icon':[]},
                'e': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'icon':[]}}}

        for day in weather_data['forecasts']:
            for hour in day['hours']:
                date = datetime.fromtimestamp(hour['hour_ts'])
                if date >= not_before and date <= not_after:
                    day_part = self.__get_daypart(date)
                    if day_part not in summary['order']:
                        summary['order'].append(day_part)
                    summary['parts'][day_part]['temp'].append(hour['temp'])                      # +11
                    summary['parts'][day_part]['humidity'].append(hour['humidity'])
                    #summary['parts'][day_part]['pressure'].append(hour['pressure'])
                    summary['parts'][day_part]['wind_speed'].append(hour['wind_speed'])
                    summary['parts'][day_part]['wind_deg'].append(hour['wind_angle'])
                    summary['parts'][day_part]['cast'].append(hour['condition'])                  # Clouds
                    #summary['parts'][day_part]['description'].append(hour[''])                    # scattered clouds
                    summary['parts'][day_part]['icon'].append(hour['icon'])                       # 03d

        for s_key in summary['parts']:
            for key in summary['parts'][s_key]:
                if key == 'temp':
                    min_t = round(min(summary['parts'][s_key][key]))
                    max_t = round(max(summary['parts'][s_key][key]))
                    if max_t - min_t > 1:
                        summary['parts'][s_key][key] = '{}°..{}°'.format(self.__add_sign(min_t), self.__add_sign(max_t))
                    else:
                        summary['parts'][s_key][key] = '{}°'.format(self.__add_sign(round(self.__average(summary['parts'][s_key][key]))))
                elif key == 'wind_speed':
                    tmp = self.__average(summary['parts'][s_key][key])
                    summary['parts'][s_key][key] = '{}'.format(round(tmp)) if tmp is not None else tmp
                elif key in ('humidity', 'pressure', 'wind_deg'):
                    tmp = self.__average(summary['parts'][s_key][key])
                    summary['parts'][s_key][key] = round(tmp) if tmp is not None else tmp
                else:
                    summary['parts'][s_key][key] = self.__most_common(summary['parts'][s_key][key])

        return summary

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    yw = YW()
    forecast = yw.get_forecast(('55.755864', '37.617698'))
    print(json.dumps(forecast, indent=4, sort_keys=True, default=str, ensure_ascii=False))
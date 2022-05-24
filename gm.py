#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime, timedelta
from pprint import pprint
from gm_cfg import token

logger = logging.getLogger(__name__)

class GM:

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
        return max(set(lst), key = lst.count)

    @staticmethod
    def __average(lst):
        return sum(lst) / len(lst)

    @staticmethod
    def __add_sign(num):
        if num > 0:
            sign = '+'
        else:
            sign = ''
        return sign+str(num)

    def get_forecast(self, coord):
        headers = {'X-Gismeteo-Token': token,
                   'Accept-Encoding': 'deflate'}
        payload = {
            'latitude': coord[0],
            'longitude': coord[1],
            'days': 2,
            'lang': 'ru'}
        try:
            result = requests.get('https://api.gismeteo.net/v2/weather/forecast', headers=headers, params=payload, timeout=(10,30))
        except Exception as e:
            logger.error('Error getting weather forecast data')
            return {}
        else:
            logger.info('Weather forecast data received successfully')

        weather_data = result.json()

        now = datetime.now()
        hour = int(now.strftime('%-H'))
        not_before = now.replace(hour=hour - hour % 6, minute=0, second=0, microsecond=0)
        not_after = not_before + timedelta(hours=23)

        summary = {
            'order' : [],
            'parts': {
                'n': {'temp':[], 'cast':[], 'description':[], 'icon':[]},
                'm': {'temp':[], 'cast':[], 'description':[], 'icon':[]},
                'd': {'temp':[], 'cast':[], 'description':[], 'icon':[]},
                'e': {'temp':[], 'cast':[], 'description':[], 'icon':[]}}}

        for item in weather_data['response']:
            date = datetime.fromtimestamp(item['date']['unix'])
            if date >= not_before and date <= not_after:
                day_part = self.__get_daypart(date)
                if day_part not in summary['order']:
                    summary['order'].append(day_part)
                summary['parts'][day_part]['temp'].append(item['temperature']['air']['C'])    # +11
                summary['parts'][day_part]['cast'].append(item['cloudiness']['type'])         # Clouds
                summary['parts'][day_part]['description'].append(item['description']['full']) # scattered clouds
                summary['parts'][day_part]['icon'].append(item['icon'])                       # 03d

        for s_key in summary['parts']:
            for key in summary['parts'][s_key]:
                if key == 'temp':
                    min_t = round(min(summary['parts'][s_key][key]))
                    max_t = round(max(summary['parts'][s_key][key]))
                    if max_t - min_t > 1:
                        summary['parts'][s_key][key] = '{}..{}'.format(self.__add_sign(min_t), self.__add_sign(max_t))
                    else:
                        summary['parts'][s_key][key] = self.__add_sign(round(self.__average(summary['parts'][s_key][key])))
                else:
                    summary['parts'][s_key][key] = self.__most_common(summary['parts'][s_key][key])

        return summary

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    gw = GM()
    forecast = gw.get_forecast(('55.755864', '37.617698'))
    pprint(forecast)
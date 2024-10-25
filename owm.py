#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import requests
from datetime import datetime, timedelta
from owm_cfg import api_key
import json

logger = logging.getLogger(__name__)

class OWM:

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
        payload = {
            'lat': coord[0],
            'lon': coord[1],
            'appid': api_key,
            'units': 'metric',
            'lang': 'ru',
            'exclude': 'current,minutely,daily'}
        try:
            result = requests.get('https://api.openweathermap.org/data/2.5/onecall', params=payload, timeout=(10,30))
        except Exception as e:
            logger.error('Error getting weather forecast data')
            return {}
        else:
            weather_data = result.json()
            logger.info('Weather forecast data received successfully')

        until = datetime.now() + timedelta(hours=23)

        summary = {
            'order' : [],
            'parts': {
                'n': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'code':[], 'icon':[]},
                'm': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'code':[], 'icon':[]},
                'd': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'code':[], 'icon':[]},
                'e': {'temp':[], 'humidity':[], 'pressure':[], 'wind_speed':[], 'wind_deg':[], 'cast':[], 'description':[], 'code':[], 'icon':[]}}}

        for item in weather_data.get('hourly'):
            date = datetime.fromtimestamp(item['dt'])
            if date <= until:
                day_part = self.__get_daypart(date)
                if day_part not in summary['order']:
                    summary['order'].append(day_part)
                summary['parts'][day_part]['temp'].append(item['temp'])
                summary['parts'][day_part]['humidity'].append(item['humidity'])
                summary['parts'][day_part]['pressure'].append(item['pressure'])
                summary['parts'][day_part]['wind_speed'].append(item['wind_speed'])
                summary['parts'][day_part]['wind_deg'].append(item['wind_deg'])
                summary['parts'][day_part]['cast'].append(item['weather'][0]['main'])
                summary['parts'][day_part]['description'].append(item['weather'][0]['description'])
                summary['parts'][day_part]['code'].append(item['weather'][0]['id'])
                summary['parts'][day_part]['icon'].append(item['weather'][0]['icon'])
            else:
                break

        for s_key in summary['parts']:
            for key in summary['parts'][s_key]:
                if key == 'temp':
                    min_t = round(min(summary['parts'][s_key][key]))
                    max_t = round(max(summary['parts'][s_key][key]))
                    if max_t - min_t > 1:
                        summary['parts'][s_key][key] = '{}°..{}°'.format(self.__add_sign(min_t), self.__add_sign(max_t))
                    else:
                        summary['parts'][s_key][key] = '{}°'.format(self.__add_sign(round(self.__average(summary['parts'][s_key][key]))))
                elif key == 'pressure':
                    summary['parts'][s_key][key] = round(self.__average(summary['parts'][s_key][key])/1.333)
                elif key in ('humidity' 'wind_speed', 'wind_deg'):
                    summary['parts'][s_key][key] = round(self.__average(summary['parts'][s_key][key]))
                else:
                    summary['parts'][s_key][key] = self.__most_common(summary['parts'][s_key][key])

        return summary

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    owm = OWM()
    forecast = owm.get_forecast(('55.755864', '37.617698'))
    print(json.dumps(forecast, indent=4, sort_keys=True, default=str, ensure_ascii=False))
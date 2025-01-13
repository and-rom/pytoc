#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import requests
import json
from datetime import date, datetime, timedelta

if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    year = datetime.today().strftime('%Y')
year = int(year)

url = f'https://isdayoff.ru/api/getdata?year={year}'
result = requests.get(url)
if result.status_code != 200:
    print('Request isdayoff.ru returned non 200 code')
    sys.exit(1)

days = list(result.text)

_date = date(year, 1, 1)

daysOff = []
for day in days:
    d = int(_date.strftime('%d'))
    m = int(_date.strftime('%m')) - 1
    if day == '1':
        if len(daysOff) < m + 1:
            daysOff.insert(m, [])
        daysOff[m].append(d)
    _date = _date + timedelta(days = 1)

with open(f'holidays_{year}.json', 'r+') as jsonf:
    json_data = json.load(jsonf)
    json_data['daysOff'] = daysOff
    jsonf.seek(0)
    jsonf.write(json.dumps(json_data, sort_keys=True, indent=2, ensure_ascii=False))
    jsonf.truncate()
    jsonf.close()
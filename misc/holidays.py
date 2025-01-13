#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys
import csv
import json
from datetime import datetime

if len(sys.argv) > 1:
    year = sys.argv[1]
else:
    year = datetime.today().strftime('%Y')

holidays = []

with open(f'holidays_{year}.csv', 'r') as csvf:
    csv_reader = csv.DictReader(csvf, delimiter=';')
    for row in csv_reader:
        m = int(row['month']) - 1
        d = int(row['day']) - 1
        if len(holidays) < m + 1:
            holidays.insert(m, [])
        if row['X'] != '?':
            holiday = {
                'title': row['title'],
                'dayoff': row['dayoff'] == 'true',
                'type': row['type']
            }
        else:
            holiday = {
                'title': '',
                'dayoff': False,
                'type': ''
            }
        holidays[m].insert(d, holiday)
    csvf.close()

with open(f'holidays_{year}.csv', 'r+') as jsonf:
    json_data = json.load(jsonf)
    json_data['holidays'] = holidays
    jsonf.seek(0)
    jsonf.write(json.dumps(json_data, sort_keys=True, indent=2, ensure_ascii=False))
    jsonf.truncate()
    jsonf.close()

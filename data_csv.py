#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import csv
import json
from pprint import pprint

p = os.path.dirname(os.path.realpath(__file__))

holidays = []

with open(os.path.join(p, 'misc', 'cal.csv'), 'r') as csvf:
    csv_reader = csv.DictReader(csvf, delimiter=';')
    for row in csv_reader:
        if len(holidays) <= int(row['month'])-1:
            holidays.insert(int(row['month'])-1, [])
        holidays[int(row['month'])-1].insert(int(row['day'])-1, {'title': row['title'], 'dayoff': row['dayoff'] == 'true', 'type': row['type']})
    csvf.close()

with open(os.path.join(p, 'data', 'cal.json'), 'r+') as jsonf:
    json_data = json.load(jsonf)
    json_data['holidays'] = holidays
    jsonf.seek(0)
    jsonf.write(json.dumps(json_data, sort_keys=True, indent=2, ensure_ascii=False))
    jsonf.truncate()
    jsonf.close()

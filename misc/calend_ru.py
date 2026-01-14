#!/usr/bin/env python3
# -*- coding: utf-8 -*-

def calend_ru(d, m, date, isdayoff):
    import requests
    from lxml import etree



    result = requests.get(f'https://www.calend.ru/holidays/{m}-{d}/')
    tree = etree.HTML(result.content)
    h_list = tree.xpath('//div[contains(@class, "datesList")]/div[contains(@class, "holidays")]/ul/li')
    for h in h_list:
        h_type = h.xpath('./div[contains(@class, "caption")]/div[contains(@class, "link")]/a')[0].attrib['href'].replace('/holidays/','').replace('/', '')
        if h_type not in ['orthodox', 'russtate', 'slav', 'un', 'wholeworld']:
            continue
        h_type = h_type.replace('wholeworld', 'int').replace('russtate', 'rus').replace('orthodox', 'rel')
        h_title = h.xpath('./div[contains(@class, "caption")]/span[contains(@class, "title")]/a')[0].text
        print(f'{date};{d};{m};{h_title};{isdayoff};{h_type}')
        #print(f'{h_type}')
    #print()

def main():
    import json
    from datetime import datetime, timedelta

    year = 2026

    with open(f'holidays_{year}.json', 'r+') as jsonf:
        json_data = json.load(jsonf)
        daysOff = json_data['daysOff']

    start_date = datetime(year, 1, 1)
    end_date = datetime(year, 12, 31)

    current_date = start_date
    while current_date <= end_date:
        calend_ru(
            current_date.day,
            current_date.month,
            current_date.strftime('%d.%m.%Y'),
            str(current_date.day in daysOff[current_date.month-1]).lower()
        )

        current_date += timedelta(days=1)

if __name__ == "__main__":
    main()
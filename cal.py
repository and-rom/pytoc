#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import random
from sheet import TearOffCalendarSheet
from backpage.xkcd import XKCD
from backpage.bashorg import BashOrg

parser = argparse.ArgumentParser(prog='pytoc', description='Python Tear-Off Calendar', usage='%(prog)s [options]')

parser.add_argument('-t', '--template', dest='template', help='name of calendar sheet template')
parser.add_argument('-i', '--image', dest='image', help='path for image when there is no screen', default='.')
parser.add_argument('-b', '--back', dest='back', help='display back image on screen', action='store_true')
parser.add_argument('-f', '--front', dest='front', help='display front image on screen', action='store_true')
parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR')

parser._optionals.title = 'Options'

args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log_level), format='%(levelname)s - %(name)s - %(message)s')

sheet = TearOffCalendarSheet(args.image)
if not args.back:
    if not args.front:
        backpages = [XKCD, BashOrg]
        backsheet = random.choice(backpages)(args.image)

        sheet.backpage_name = backsheet.name
        sheet.draw()
        backsheet.draw()
    else:
        sheet.redraw()
else:
    sheet.draw_back()
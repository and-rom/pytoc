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
parser.add_argument('-bi', '--back-image', dest='back_image', help='path for back image', default='.')
parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR')

parser._optionals.title = 'Options'

args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log_level), format='%(levelname)s - %(name)s - %(message)s')

sheet = TearOffCalendarSheet(args.image, args.back_image)
if not args.back:
    sheet.draw()

    backpages = [XKCD, BashOrg]

    backsheet = random.choice(backpages)(args.back_image)
    backsheet.draw()
else:
    sheet.draw_back()
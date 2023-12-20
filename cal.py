#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import random
from backpage.dummy import Dummy
from backpage.xkcd import XKCD
from backpage.bashorg import BashOrg

parser = argparse.ArgumentParser(prog='pytoc', description='Python Tear-Off Calendar', usage='%(prog)s [options]')

parser.add_argument('-t', '--template', dest='template', help='name of calendar sheet template', default='1')
parser.add_argument('-i', '--image', dest='image', help='path for images', default='.')
parser.add_argument('-b', '--back', dest='back', help='display back image on screen', action='store_true')
parser.add_argument('-f', '--front', dest='front', help='display front image on screen', action='store_true')
parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR')

parser._optionals.title = 'Options'

args = parser.parse_args()

logging.basicConfig(level=getattr(logging, args.log_level), format='%(levelname)s - %(name)s - %(message)s')
logger = logging.getLogger("cal")

sheet = __import__('sheet_' + args.template, globals(), locals(), ['TearOffCalendarSheet']).TearOffCalendarSheet(args.image)
if not args.back:
    if not args.front:
        if "7in5" in args.template:
            backpages = [Dummy]
        else:
            backpages = [XKCD, Dummy]
        backsheet = random.choice(backpages)(w = sheet.page_w, h = sheet.page_h, image_path = args.image)

        sheet.backpage_name = backsheet.name
        sheet.draw()
        try:
            backsheet.draw()
        except SystemError as e:
            logger.error(e)
        sheet.display_front()
    else:
        sheet.display_front()
else:
    sheet.display_back()
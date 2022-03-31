#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from sheet import TearOffCalendarSheet

parser = argparse.ArgumentParser(prog='pytoc', description='Python Tear-Off Calendar', usage='%(prog)s [options]')

parser.add_argument('-t', '--template', dest='template', help='name of calendar sheet template')
parser.add_argument('-i', '--image', dest='image', help='path for image when there is no screen', default='.')
parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR')

parser._optionals.title = 'Options'

args = parser.parse_args()

print(args.log_level)

logging.basicConfig(level=getattr(logging, args.log_level))
sheet = TearOffCalendarSheet(args.image)
sheet.draw()
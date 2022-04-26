#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os, sys, traceback
import signal
import argparse
import logging
import RPi.GPIO as GPIO
from sheet import TearOffCalendarSheet
from time import sleep

def quit(signalNumber = None, frame = None):
    logger.info('Quit')
    if signalNumber is not None:
        sys.exit(0)
    else:
        return 0

def main():
    global logger

    signal.signal(signal.SIGTERM, quit)
    try:
        parser = argparse.ArgumentParser(prog='pytoc', description='Python Tear-Off Calendar', usage='%(prog)s [options]')

        parser.add_argument('-p', '--pin', dest='buttonPin', help='GPIO pin number', type=int)
        parser.add_argument('-i', '--image', dest='image', help='path for images', default='.')
        parser.add_argument('-l', '--log-level', dest='log_level', choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'], default='ERROR')

        parser._optionals.title = 'Options'

        args = parser.parse_args()

        logging.basicConfig(level=getattr(logging, args.log_level), format='%(levelname)s - %(name)s - %(message)s')
        logger = logging.getLogger('btn')

        GPIO.setmode(GPIO.BCM)

        buttonPin = args.buttonPin

        GPIO.setup(buttonPin, GPIO.IN,pull_up_down=GPIO.PUD_UP)

        sheet = TearOffCalendarSheet(args.image)

        lock = False
        back = False
        while True:
            buttonState = GPIO.input(buttonPin)
            if (buttonState == GPIO.HIGH and not lock):
                lock = True
                if not back:
                    print('sheet.display_back()')
                    logger.info('Back drawn')
                    back = True
                else:
                    print('sheet.display_front()')
                    logger.info('Front drawn')
                    back = False
            if (buttonState == GPIO.LOW and lock):
                lock = False
            sleep(0.1);
    except KeyboardInterrupt:
        return quit()
    except Exception:
        traceback.print_exc(file=sys.stdout)
        return 1

if __name__ == "__main__":
    sys.exit(main())
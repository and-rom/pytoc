#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

def get_quality():
    interface = "wlan0"
    keyword = "Link Quality="

    proc = subprocess.Popen(["iwconfig", interface],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    for line in out.split('\n'):
        line=line.lstrip()
        length=len(keyword)
        if line[:length] == keyword:
            quality = line[length:].split()[0].split('/')
            return str(int(round(float(quality[0]) / float(quality[1]) * 100)))

if __name__=='__main__':
    print(get_quality())
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import subprocess

def get_quality(device):
    keyword = "Link Quality="

    proc = subprocess.Popen(["iwconfig", device],stdout=subprocess.PIPE, universal_newlines=True)
    out, err = proc.communicate()

    for line in out.split('\n'):
        line=line.lstrip()
        length=len(keyword)
        if line[:length] == keyword:
            quality = line[length:].split()[0].split('/')
            return int(round(float(quality[0]) / float(quality[1]) * 100))
        else:
            return None

if __name__=='__main__':
    print(get_quality('wlan0'))
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jul 24 08:49:34 2020

@author: mashanmu
"""

from ShiJiuZhong import ShiJiuZhong
from MiniSEED import MiniSEED
from Taide import Taide
import asyncio

loop = asyncio.get_event_loop()

fileUrl = '/Users/mashanmu/Desktop/十九中数据转换/十九中振动监测_20200712063859.txt'
fileName = '2020-07-02 06:38:59.txt'

DataTrans = ShiJiuZhong(fileUrl, fileName)
loop.run_until_complete(DataTrans.update(fileUrl, fileName))

print("runhere")
#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: tools.py
@time: 2017/7/1 14:40
"""

import datetime


def get_one_day(period):
    today = datetime.date.today()
    one_day = datetime.timedelta(days=period)
    target_day = today - one_day
    return target_day.strftime("%Y-%m-%d")


def get_now_time():
    from datetime import datetime
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_start_time(date):
    return date + " 00:00:00"


def get_end_time(date):
    return date + " 23:59:59"

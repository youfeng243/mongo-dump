#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: export.py
@time: 2017/10/28 10:24
"""
import json

from config import app_data_config

app_data_table = 'enterprise_data_gov'

dump_date_tmp_path = '/home/youfeng/dump_data/'

start_time = '2017-10-28 09:30:00'

cmd = "./mongoexport -h " + app_data_config["host"] + ":" + str(app_data_config["port"]) + " -d " + \
                  app_data_config[
                      "db"] + " -c " + app_data_table + " -u " + app_data_config["username"] + " -p " + app_data_config[
                      "password"] + " -o " + dump_date_tmp_path + app_data_table + ".json" + " -q "
cmd += "'" + json.dumps(
    {"$and": [{"_utime": {"$gte": start_time}}]}) + "'"

print cmd
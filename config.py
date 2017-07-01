#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: config.py
@time: 2017/7/1 14:17
"""
# 业务数据库
app_data_config = {
    "host": "172.16.215.16",
    "port": 40042,
    "db": "app_data",
    "username": "read",
    "password": "read",
}

# 数据同步记录
data_sync_config = {
    "host": "172.16.215.2",
    "port": 40042,
    "db": "data_sync",
    "username": "work",
    "password": "haizhi",
}

# 导出周期 半小时统计一次
sleep_time = 1800

# 校验周期
check_period = 3


# 记录表前置标识
dump_table_flag = "dump_"

# 数据导出路径
dump_path = "/home/nfs/server-download-dir/mongodb-dump/"
#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: main.py
@time: 2017/7/1 12:27
"""
import subprocess
import sys
import time

import tools
from config import app_data_config, sleep_time, check_period, data_sync_config, dump_table_flag, dump_path
from logger import Logger
from mongo import MongDb

log = Logger("mongo-dump.log").get_logger()

app_data = MongDb(app_data_config['host'], app_data_config['port'], app_data_config['db'],
                  app_data_config['username'],
                  app_data_config['password'], log=log)

data_sync = MongDb(data_sync_config['host'], data_sync_config['port'], data_sync_config['db'],
                   data_sync_config['username'],
                   data_sync_config['password'], log=log)


# 获得所有的表信息
def get_all_table_name():
    return app_data.collection_names()


# 运行命令
def run_cmd(cmd):
    res = ''
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline()
        res += line
        if line:
            sys.stdout.flush()
        else:
            break
    p.wait()
    return res


# 删除所有任务
def remove_all_task():
    table_list = get_all_table_name()

    for app_data_table in table_list:
        dump_table_name = dump_table_flag + app_data_table
        data_sync.drop(dump_table_name)

    log.info("删除所有表成功, 开始休眠10s")
    time.sleep(10)


# 分解任务
def split_dump_task():
    log.info("分解任务开始...")
    start_time = time.time()
    table_list = get_all_table_name()

    # 生成任务信息
    for period in xrange(1, check_period + 1):
        # 获得日期信息
        _id = tools.get_one_day(period)

        for app_data_table in table_list:
            dump_table_name = dump_table_flag + app_data_table
            if data_sync.find_one(dump_table_name, {"_id": _id}) is None:
                task_item = {
                    "_id": _id,
                    "finish": False,
                    "createTime": tools.get_now_time(),
                    "updateTime": tools.get_now_time(),
                    "startTime": tools.get_start_time(_id),
                    "endTime": tools.get_end_time(_id)
                }
                data_sync.insert(dump_table_name, task_item)

    log.info("分解任务执行完成..")
    end_time = time.time()
    log.info('分解任务消耗时间: {t}s'.format(t=end_time - start_time))


# 当前单进程执行导出任务
def execute_dump_task():
    log.info("导出任务开始...")
    start_time = time.time()

    table_list = get_all_table_name()

    for period in xrange(1, check_period + 1):
        date = tools.get_one_day(period)

        # 确保批次文件夹是否已经存在
        run_cmd("mkdir -p {path}".format(path=dump_path + date))

    log.info("导出任务执行完成..")
    end_time = time.time()
    log.info('导出任务消耗时间: {t}s'.format(t=end_time - start_time))


def main():
    # remove_all_task()

    while True:
        start_time = time.time()
        log.info("开始执行dump任务..")

        # 分解任务
        split_dump_task()

        # 执行导出任务
        execute_dump_task()

        log.info("dump任务执行完成..")
        end_time = time.time()
        log.info('dump任务消耗时间: {t}s'.format(t=end_time - start_time))

        # 休眠时间
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()

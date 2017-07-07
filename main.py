#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: main.py
@time: 2017/7/1 12:27
"""
import json
import subprocess
import sys
import time

import tools
from config import app_data_config, sleep_time, check_period, data_sync_config, dump_table_flag, dump_path, \
    dump_status_file_name, dump_tmp_path
from logger import Logger
from mongo import MongDb

log = Logger("mongo-dump.log").get_logger()

app_data = MongDb(app_data_config['host'], app_data_config['port'], app_data_config['db'],
                  app_data_config['username'],
                  app_data_config['password'], log=log)

data_sync = MongDb(data_sync_config['host'], data_sync_config['port'], data_sync_config['db'],
                   data_sync_config['username'],
                   data_sync_config['password'], log=log)

TABLE_CONFIG = "table.config"


# 获得所有的表信息
def get_all_table_name():
    table_set = set()
    with open(TABLE_CONFIG) as p_file:
        for line in p_file:
            table_name = line.strip().strip("\r").strip("\n")
            table_set.add(table_name)

    return list(table_set)


# 运行命令
def run_cmd(cmd):
    log.info(cmd)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = p.stdout.readline()
        log.info(line)
        if line:
            sys.stdout.flush()
        else:
            break
    p.wait()


# 删除所有任务
def remove_all_task():
    for table_name in data_sync.collection_names():
        if dump_table_flag in table_name:
            data_sync.drop(table_name)

    log.info("删除所有表成功, 开始休眠10s")
    exit()


# 记录导出文件状态
def record_status_file(date, dump_table_list):
    full_path = dump_path + date + "/"
    status_file_path = full_path + dump_status_file_name

    # 已经存在表的信息
    exists_table_set = set()

    with open(status_file_path) as p_file:
        for line in p_file:
            file_name = line.strip().strip("\r").strip("\n")
            table_name = file_name.split(".")[0]
            exists_table_set.add(table_name)

    # 如果文件以及存在 则不再写入
    # if os.path.exists(status_file_path):
    #     return

    if len(exists_table_set) <= 0:
        # 确保批次文件夹是否已经存在
        run_cmd("mkdir -p {path}".format(path=dump_path + date))

    is_all_in_file = True
    for table_name in dump_table_list:
        if table_name not in exists_table_set:
            is_all_in_file = False
            break

    # 开始记录状态信息
    if not is_all_in_file:
        with open(status_file_path, mode="w") as p_file:
            for name in dump_table_list:
                p_file.write(name + ".zip" + "\r\n")


# 分解任务
def split_dump_task():
    log.info("分解任务开始...")
    start_time = time.time()
    table_list = get_all_table_name()

    dump_table_list = list()
    for app_data_table in table_list:
        dump_table_list.append(app_data_table)

    # 生成任务信息
    for period in xrange(1, check_period + 1):
        # 获得日期信息
        _id = tools.get_one_day(period)

        # 写入列表信息
        record_status_file(_id, dump_table_list)

        for app_data_table in table_list:
            dump_table_name = dump_table_flag + app_data_table
            search_item = data_sync.find_one(dump_table_name, {"_id": _id})
            if search_item is None:
                task_item = {
                    "_id": _id,
                    "finish": False,
                    "createTime": tools.get_now_time(),
                    "updateTime": tools.get_now_time(),
                    "startTime": tools.get_start_time(_id),
                    "endTime": tools.get_end_time(_id)
                }
                data_sync.insert(dump_table_name, task_item)
                continue

    log.info("分解任务执行完成..")
    end_time = time.time()
    log.info('分解任务消耗时间: {t}s'.format(t=end_time - start_time))


# 当前单进程执行导出任务
def execute_dump_task():
    log.info("导出任务开始...")
    start_exec_time = time.time()

    # 获得全部表信息
    table_list = get_all_table_name()

    # 根据日期开始导出数据
    for period in xrange(check_period, 0, -1):
        # 获得日期信息
        _id = tools.get_one_day(period)

        # 遍历表导出
        for app_data_table in table_list:
            dump_table_name = dump_table_flag + app_data_table

            task_item = data_sync.find_one(dump_table_name, {'_id': _id})
            if task_item is None:
                continue

            if task_item['finish']:
                continue

            # 获得未完成的任务列表信息
            # for task_item in data_sync.traverse(dump_table_name, {'finish': False}):
            start_time = task_item["startTime"]
            end_time = task_item["endTime"]
            date = task_item["_id"]

            # 导出临时路径
            dump_date_tmp_path = dump_tmp_path + date + "/"
            run_cmd("mkdir -p {path}".format(path=dump_date_tmp_path))

            # 删除已经存在的数据
            run_cmd("rm -rf {source}{table}.json".format(
                source=dump_date_tmp_path,
                table=app_data_table))
            # 删除存在的压缩包
            run_cmd("rm -rf {source}{table}.zip".format(
                source=dump_date_tmp_path,
                table=app_data_table))

            cmd = "./mongoexport -h " + app_data_config["host"] + ":" + str(app_data_config["port"]) + " -d " + \
                  app_data_config[
                      "db"] + " -c " + app_data_table + " -u " + app_data_config["username"] + " -p " + app_data_config[
                      "password"] + " -o " + dump_date_tmp_path + app_data_table + ".json" + " -q "
            cmd += "'" + json.dumps(
                {"$and": [{"_utime": {"$gte": start_time}}, {"_utime": {"$lte": end_time}}]}) + "'"

            # 开始执行导出任务
            run_cmd(cmd)

            # 移动文件
            target_path = dump_path + date + "/"
            run_cmd("mkdir -p {path}".format(path=target_path))

            # 压缩数据
            run_cmd("zip {source}{table}.zip {source}{table}.json".format(
                source=dump_date_tmp_path,
                table=app_data_table))

            # 移动数据
            run_cmd("mv -f {source}{table}.zip {target_path}".format(
                source=dump_date_tmp_path,
                table=app_data_table,
                target_path=target_path))

            # 删除文件
            run_cmd("rm -rf {source}{table}.json".format(
                source=dump_date_tmp_path,
                table=app_data_table))

            # 删除存在的压缩包
            run_cmd("rm -rf {source}{table}.zip".format(
                source=dump_date_tmp_path,
                table=app_data_table))

            task_item["finish"] = True
            task_item["updateTime"] = tools.get_now_time()

            # 记录状态
            data_sync.insert_batch_data(dump_table_name, [task_item])

    log.info("导出任务执行完成..")
    end_exec_time = time.time()
    log.info('导出任务消耗时间: {t}s'.format(t=end_exec_time - start_exec_time))


# 创建索引
def ensure_index():
    table_list = get_all_table_name()

    for app_data_table in table_list:
        dump_table_name = dump_table_flag + app_data_table
        data_sync.create_index(dump_table_name, [('finish', MongDb.ASCENDING)])


def main():
    # remove_all_task()

    while True:
        start_time = time.time()
        log.info("开始执行dump任务..")

        # 分解任务
        split_dump_task()

        # 创建索引
        ensure_index()

        # 执行导出任务
        execute_dump_task()

        log.info("dump任务执行完成..")
        end_time = time.time()
        log.info('dump任务消耗时间: {t}s'.format(t=end_time - start_time))

        # 休眠时间
        time.sleep(sleep_time)


if __name__ == '__main__':
    main()

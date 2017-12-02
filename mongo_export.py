#!/usr/bin/env python
# encoding: utf-8
"""
@author: youfeng
@email: youfeng243@163.com
@license: Apache Licence
@file: mongo_export.py
@time: 2017/12/1 21:29
"""
import os
import subprocess
import sys

from logger import Logger
from mongo import MongDb

app_data_conf = {
    'host': '172.16.215.16',
    'port': 40042,
    'db': 'app_data',
    'username': 'work',
    'password': 'haizhi',
}

# company_data 海致配置
company_data_conf = {
    'host': '172.16.215.2',
    'port': 40042,
    'db': 'company_data',
    'username': 'work',
    'password': 'haizhi',
}
log = Logger('export_data.log').get_logger()

# 配置文件文件夹
CONFIG_FOLDER_PATH = './table_list'
DUMP_DATA_FOLDER_PATH = './dum_list'

SEARCH_KEY = {
    'enterprise_data_gov': 'company',
    'judgement_wenshu': 'litigant_list',
    'court_ktgg': 'litigant_list',
    'judge_process': 'litigant_list',
    'zhixing_info': 'i_name',
    'bulletin': 'litigant_list',
}


class Dump(object):
    def __init__(self, config_folder_path, dump_data_folder_path):
        # 创建dump数据文件夹
        if not os.path.exists(dump_data_folder_path):
            os.makedirs(dump_data_folder_path)

        self.app_data_db = MongDb(app_data_conf['host'], app_data_conf['port'], app_data_conf['db'],
                                  app_data_conf['username'], app_data_conf['password'], log=log)

        self.company_data_db = MongDb(company_data_conf['host'], company_data_conf['port'], company_data_conf['db'],
                                      company_data_conf['username'], company_data_conf['password'], log=log)

        self.config_folder_path = config_folder_path
        self.dump_data_folder_path = dump_data_folder_path

        self.search_key = SEARCH_KEY

        # 获得配置文件列表
        self.file_list = self.get_file_list(config_folder_path)

        # 获得导出程序完整路径
        self.export_full_path = './bin/{}/mongoexport'.format(self.get_os_info())
        log.info("导出程序路径为: {}".format(self.export_full_path))

        self.dump_process(self.file_list)

    @staticmethod
    def get_file_list(file_path):
        file_list = []
        if not os.path.isdir(file_path):
            log.error("文件路径不存在: {}".format(file_path))
            return file_list

        return os.listdir(file_path)

    # 获得系统信息
    @staticmethod
    def get_os_info():
        import platform
        system = platform.system()
        if system == 'Darwin':
            return 'mac'
        if system == 'Linux':
            return 'linux'
        return 'linux'

    @staticmethod
    def parse_table_name(file_name):
        return file_name.split('.')[0]

    # 获得需要dump且不存在的临时表名
    def get_dump_table_name(self, table_name):
        version = 1
        dump_table_name = 'temp_dump_data_' + table_name
        while True:

            # 判断当前表是否存在
            if self.app_data_db.select_count(dump_table_name) == 0:
                return dump_table_name

            dump_table_name = 'temp_dump_data_{}_{}'.format(table_name, version)
            version += 1

    @staticmethod
    def get_company_list(config_file_path):
        company_list = []
        with open(config_file_path, 'r') as p_file:
            for line in p_file:
                company = line.strip().strip('\n').strip('\r')
                company_list.append(company)

        log.info("当前配置文件企业数目: company num = {} config = {}".format(len(company_list), config_file_path))
        return company_list

    @staticmethod
    def get_replace_name(company):
        replace_name_1 = company.replace('(', '（').replace(')', '）')
        replace_name_2 = company.replace('（', '(').replace('）', ')')
        return replace_name_1, replace_name_2

    def copy_data_to_dump_table(self, company_list, source_table, target_table):
        count = 0
        log.info("开始复制数据...")
        result_list = []
        for company in company_list:
            count += 1
            replace_company1, replace_company2 = self.get_replace_name(company)
            search_list = []
            if replace_company1 == replace_company2:
                search_list.append(replace_company1)
            else:
                search_list.append(replace_company1)
                search_list.append(replace_company2)

            find_count = 0
            for search_name in search_list:
                for item in self.app_data_db.traverse(source_table, {self.search_key[source_table]: search_name}):
                    find_count += 1
                    result_list.append(item)
                    if len(result_list) >= 500:
                        self.company_data_db.insert_batch_data(target_table, result_list)
                        del result_list[:]
            if find_count <= 0:
                log.error("没有搜索到任何信息: {} {}".format(source_table, company))
            # try:
            #     if replace_company1 == replace_company2:
            #         item = self.app_data_db.find_one(source_table, {'company': replace_company1})
            #         if item is not None:
            #             self.company_data_db.insert(target_table, item)
            #         else:
            #             log.error("当前企业没有搜索到任何信息: {}".format(company))
            #     else:
            #         item1 = self.app_data_db.find_one(source_table, {'company': replace_company1})
            #         if item1 is not None:
            #             self.company_data_db.insert(target_table, item1)
            #         item2 = self.app_data_db.find_one(source_table, {'company': replace_company2})
            #         if item2 is not None:
            #             self.company_data_db.insert(target_table, item2)
            #         if item1 is None and item2 is None:
            #             log.error("当前企业没有搜索到任何信息: {}".format(company))
            if count % 100 == 0:
                log.info("当前进度: count = {}".format(count))
                # except Exception as e:
                #     log.error("数据迁移错误: compnay = {}".format(company))
                #     log.exception(e)
        if len(result_list) >= 0:
            self.company_data_db.insert_batch_data(target_table, result_list)
        log.info("数据复制完成: {} {}".format(source_table, target_table))

    # 运行命令
    @staticmethod
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

    # 开始dump数据
    def dump_data(self, dump_table_name, table_name):
        count = self.company_data_db.select_count(dump_table_name)
        log.info("当前导出数据量为: table_name = {} count = {}".format(table_name, count))
        if count > 0:
            cmd = self.export_full_path + " -h " + company_data_conf["host"] + ":" + str(
                company_data_conf["port"]) + " -d " + \
                  company_data_conf[
                      "db"] + " -c " + dump_table_name + " -u " + company_data_conf["username"] + " -p " + \
                  company_data_conf[
                      "password"] + " -o " + self.dump_data_folder_path + '/' + table_name + ".json"
            self.run_cmd(cmd)
        return count

    # 压缩数据
    def zip_data(self, table_name, dump_data_folder_path):
        try:
            zip_path = '{}/{}.zip'.format(dump_data_folder_path, table_name)
            json_path = '{}.json'.format(dump_data_folder_path + '/' + table_name)
            if os.path.exists(json_path):
                self.run_cmd("zip {} {}".format(zip_path, json_path))
                log.info("压缩数据完成: {}".format(table_name))
            else:
                log.error("当前路径json文件不存在不进行压缩: {}".format(json_path))
        except Exception as e:
            log.error("压缩数据失败: table_name = {}".format(table_name))
            log.exception(e)

    def dump_by_config(self, file_name):
        table_name = self.parse_table_name(file_name)
        dump_table_name = self.get_dump_table_name(table_name)
        config_file_path = self.config_folder_path + '/' + file_name
        log.info("需要导出的数据表: {}".format(table_name))
        log.info("临时存储表: {}".format(dump_table_name))
        log.info("企业名单配置文件路径: {}".format(config_file_path))

        # 获得企业名单
        company_list = self.get_company_list(config_file_path)

        # 复制数据
        self.copy_data_to_dump_table(company_list, table_name, dump_table_name)

        # dump 数据
        self.dump_data(dump_table_name, table_name)

        # 压缩数据
        self.zip_data(table_name, self.dump_data_folder_path)

        # 删除dump表
        self.company_data_db.drop(dump_table_name)
        log.info("临时表删除完成: {}".format(dump_table_name))

    def dump_process(self, file_list):
        for file_name in file_list:
            self.dump_by_config(file_name)


def main():
    Dump(CONFIG_FOLDER_PATH, DUMP_DATA_FOLDER_PATH)


if __name__ == '__main__':
    main()

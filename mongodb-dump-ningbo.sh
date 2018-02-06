#!/usr/bin/env bash
#judgement_wenshu

set -ex

dump_path=/home/youfeng/mongo-dump/ningbo_dump_list/

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_gs_business_scope  -u work -p haizhi  -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_gs_company_name  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_gs_legal_man  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_gs_registered_capital  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_zhaobiao_1000w  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_zhaobiao_all  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_zhongbiao_1000w  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c zhejiang_ningbo_zhongbiao_500w  -u work -p haizhi -o ${dump_path}
cd ningbo_dump_list/
zip ningbo_dump.zip -r app_data/
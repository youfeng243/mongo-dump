#!/usr/bin/env bash
#judgement_wenshu

set -ex

dump_path=/home/nfs/dump-export-tmp/mongodb-full-dump/
target_path=/home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c judgement_wenshu  -u work -p haizhi  -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c land_project_selling  -u work -p haizhi -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c investment_events  -u work -p haizhi -o ${dump_path}
# mkdir -p ${target_path}

#cd ${dump_path}
#zip judgement_wenshu.zip -r app_data/
#mv judgement_wenshu.zip ${target_path}
#echo "完成judgement_wenshu dump"
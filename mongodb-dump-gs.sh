#!/usr/bin/env bash
#enterprise_data_gov

set -ex

dump_path=/home/nfs/dump-export-tmp/mongodb-full-dump/
target_path=/home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c enterprise_data_gov  -u work -p haizhi -o ${dump_path}
mkdir -p ${target_path}

cd ${dump_path}/app_data/
zip enterprise_data_gov.zip -r *enterprise_data_gov*
mv enterprise_data_gov.zip ${target_path}
echo "完成dump"
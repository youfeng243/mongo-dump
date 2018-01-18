#!/usr/bin/env bash
#annual_reports

set -ex

dump_path=/home/youfeng/mongodb-dump/

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c annual_reports  -u work -p haizhi -o ${dump_path}


cd ${dump_path}/app_data/
zip annual_reports.zip -r *annual_reports*
echo "完成dump"
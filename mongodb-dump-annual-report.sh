#!/usr/bin/env bash
#annual_reports

set -ex

dump_path=/ssd/mongodb-dump/
target_path=/home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump
target_dump_path=/home/nfs/dump-export-tmp/mongodb-full-dump/

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c annual_reports  -u work -p haizhi -o ${dump_path}
echo "dump数据完成.."

cd ${dump_path}/app_data/
zip annual_reports.zip -r *annual_reports*
echo "数据压缩完成.."

sshpass -p youfeng243. scp annual_reports.zip youfeng@cs5:${target_dump_path}
echo "远程复制完成.."

ssh -nf cs5 "cd ${target_dump_path}; mv ${target_dump_path}annual_reports.zip ${target_path}"
echo "远程移动文件完成.."
rm -rf *annual_reports*
echo "删除文件完成.."
echo "完成dump"
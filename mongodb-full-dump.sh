#!/usr/bin/env bash
#investment_funds
#investment_institutions
#land_project_selling
#listing_events
#enterprise_data_gov_change_info

set -ex

dump_path=/home/nfs/dump-export-tmp/mongodb-full-dump/
target_path=/home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump

chmod +x mongodump
mkdir -p ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c investment_funds  -u read -p read -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c investment_institutions  -u read -p read -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c land_project_selling  -u read -p read -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c listing_events  -u read -p read -o ${dump_path}
./mongodump -h 172.16.215.16:40042 -d app_data -c enterprise_data_gov_change_info  -u read -p read -o ${dump_path}

mkdir -p ${target_path}

cd ${dump_path}
zip app_data.zip -r app_data/
mv app_data.zip ${target_path}
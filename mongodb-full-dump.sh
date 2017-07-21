#!/usr/bin/env bash
#investment_funds
#investment_institutions
#land_project_selling
#listing_events
#enterprise_data_gov_change_info

set -ex

chmod +x mongodump
mkdir -p /home/nfs/dump-export-tmp/mongodb-full-dump/
./mongodump -h 172.16.215.16:40042 -d app_data -c investment_funds  -u read -p read -o /home/nfs/dump-export-tmp/mongodb-full-dump/
./mongodump -h 172.16.215.16:40042 -d app_data -c investment_institutions  -u read -p read -o /home/nfs/dump-export-tmp/mongodb-full-dump/
./mongodump -h 172.16.215.16:40042 -d app_data -c land_project_selling  -u read -p read -o /home/nfs/dump-export-tmp/mongodb-full-dump/
./mongodump -h 172.16.215.16:40042 -d app_data -c listing_events  -u read -p read -o /home/nfs/dump-export-tmp/mongodb-full-dump/
./mongodump -h 172.16.215.16:40042 -d app_data -c enterprise_data_gov_change_info  -u read -p read -o /home/nfs/dump-export-tmp/mongodb-full-dump/

mkdir -p /home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump

cd /home/nfs/dump-export-tmp/mongodb-full-dump/
zip app_data.zip -r app_data/
mv app_data.zip /home/nfs/server-download-dir/mongodb-dump/mongodb-full-dump/
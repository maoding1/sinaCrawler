#!/bin/bash
<<EOF
作用：辅助crontab 进行定时执行，每小时执行一次。 爬取新闻内容并将日志写入log.txt
使用方法：1. 启动linux cron 服务(service cron start)
         2. crontab -e 后在文件末尾添加 1 * * * * /bin/bash [path/to/this_file] 表示每小时的第一分钟执行此脚本
         3. 使用service cron status确保cron 服务处于running状态
         4. chmod +x [path/to/this_file] 确保shell脚本具有执行权限
         5. 更改workdir变量值为项目根目录
EOF
work_dir="/root/sinaCrawler"

cd ${work_dir}

echo $(date) >> ${work_dir}/log.txt  

/usr/bin/python3 ${work_dir}/sinaCrawler.py >> ${work_dir}/log.txt 2>&1
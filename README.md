# ruijie-rlog-server
记录路由器NAT日志，方便溯源
python
记录NAT日志，每分钟保存一个文件，记录180天。

### 使用方法
1.路由器上开启rlog，配置rlog server *.*.*.*

2.在服务器上运行python脚本
nohup python3 server-liuran-180day.py > /dev/null 2> stderr.log &

3.sudo yum install gzip  

4.创建一个shell脚本compress_logs.sh
```
#!/bin/bash

log_directory="/path/to/your/log/directory"
find "$log_directory" -type f -name "*.log" -mmin +1 -exec gzip {} \;

```
```chmod +x compress_logs.sh
crontab -e
每分钟运行一次压缩
* * * * * /path/to/compress_logs.sh

```

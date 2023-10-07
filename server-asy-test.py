import socket
import asyncio
import configparser
from datetime import datetime, timedelta
import os

def get_log_file_path(log_directory):
    now = datetime.now()
    folder_name = now.strftime("%Y-%m-%d")
    file_name = now.strftime("%Y-%m-%d_%H-%M.log")
    folder_path = os.path.join(log_directory, folder_name)
    file_path = os.path.join(folder_path, file_name)
    return folder_path, file_path

def cleanup_old_logs(log_directory, max_days=180):
    oldest_allowed_date = datetime.now() - timedelta(days=max_days)
    for root, dirs, files in os.walk(log_directory):
        for dir in dirs:
            folder_date = datetime.strptime(dir, "%Y-%m-%d")
            if folder_date < oldest_allowed_date:
                folder_path = os.path.join(root, dir)
                print(f"Removing old log folder: {folder_path}")
                shutil.rmtree(folder_path)

async def handle_log_data(log_data, log_directory):
    # 创建新的日志文件
    folder_path, file_path = get_log_file_path(log_directory)
    os.makedirs(folder_path, exist_ok=True)

    # Open and close the file synchronously
    with open(file_path, 'a') as logfile:
        logfile.write(log_data + '\n')

async def rlog_server():
    config = configparser.ConfigParser()
    config.read('server.ini')

    ipaddr = config['server']['ipaddr']
    ipport = int(config['server']['port'])
    log_directory = "/data/logs"

    os.makedirs(log_directory, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ipaddr, ipport))

    while True:
        data, addr = sock.recvfrom(1024)
        log_data = data.decode('utf-8')  # 将接收到的数据解码为文本

        '''print("Received log data from", addr)
        print(log_data)'''

        # 仅将原始日志写入文件，异步执行
        await handle_log_data(log_data, log_directory)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(rlog_server())

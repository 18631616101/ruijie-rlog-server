import socket
import multiprocessing
import configparser
from datetime import datetime, timedelta
import os

def main():
    process = multiprocessing.Process(target=rlog_server, daemon=True)
    process.start()
    while True:
        pass

def get_log_file_path(log_directory):
    now = datetime.now()
    folder_name = now.strftime("%Y-%m-%d")
    file_name = now.strftime("%Y-%m-%d_%H-%M-%S.log")
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

def rlog_server():
    config = configparser.ConfigParser()
    config.read('server.ini')

    ipaddr = config['server']['ipaddr']
    ipport  = int(config['server']['port'])
    log_directory = "logs"

    os.makedirs(log_directory, exist_ok=True)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((ipaddr, ipport))

    logfile = None
    last_minute = -1

    while True:
        data, addr = sock.recvfrom(1024)
        log_data = data.decode('utf-8')  # 将接收到的数据解码为文本
        print("Received log data from", addr)
        print(log_data)

        # 解析日志数据
        log_fields = log_data.split('\t')
        log_dict = {}
        for field in log_fields:
            key, value = field.split('=')
            log_dict[key] = value

        # 提取需要的字段
        ori_src_ip = log_dict['ori_src_ip']
        ori_dst_ip = log_dict['ori_dst_ip']
        ori_src_port = log_dict['ori_src_port']
        ori_dest_port = log_dict['ori_dest_port']
        rep_src_ip = log_dict['rep_src_ip']
        rep_dst_ip = log_dict['rep_dst_ip']
        rep_src_port = log_dict['rep_src_port']
        rep_dest_port = log_dict['rep_dest_port']
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 构建日志记录
        log_rec = (
            f"ori_src_ip={ori_src_ip}\tori_dst_ip={ori_dst_ip}\tori_src_port={ori_src_port}\tori_dest_port={ori_dest_port}"
            f"\trep_src_ip={rep_src_ip}\trep_dst_ip={rep_dst_ip}\trep_src_port={rep_src_port}\trep_dest_port={rep_dest_port}"
            f"\tcreate_time={current_time}\n"
        )

        # 获取当前的分钟数
        current_minute = datetime.now().minute

        # 如果分钟数变化了，创建新的日志文件
        if current_minute != last_minute:
            last_minute = current_minute
            folder_path, file_path = get_log_file_path(log_directory)
            os.makedirs(folder_path, exist_ok=True)
            if logfile:
                logfile.close()
            logfile = open(file_path, 'a')

        # 写入到文件
        if logfile:
            logfile.write(log_rec)

        # 定期清理旧的日志文件夹
        cleanup_old_logs(log_directory)

if __name__ == '__main__':
    main()

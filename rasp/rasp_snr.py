import subprocess
import os
import sys

"""
Raspberry Pi に Send and Run します。
"""

rasp_key_path = "rasp.key"

# 送信するファイル
files = ["v_cron.sh", "v_cron.py", "v_scraper.py", "v_mysql.py", "v_liner.py", "v_mler.py"]
#files = ["v_server.sh", "v_server.py"]
#files = ["server_test.py"]
#files = ["mler_test.py"]
# files = ["mysql_test.py"]
#files = ["mysql_test2.py"]
# files = ["mysql_add_vtubers.py"]
files = ["mysql_get_info.py"]
#files = ["server.key"]

destination_dir = "~/rasp"

python_command = "python3.9"

def main():

    # 接続情報読み込み
    if os.path.isfile(rasp_key_path):
        with open(rasp_key_path, "r") as key_file:
            host = key_file.readline().splitlines()[0]
            port = key_file.readline().splitlines()[0]
            secret_key_path = key_file.readline().splitlines()[0]
    else:
        print(rasp_key_path, "does not exist.")
        sys.exit()

    if not os.path.isfile(secret_key_path):
        print(secret_key_path, "does not exist.")
        sys.exit()

    # 送信先フォルダ確認
    process = subprocess.run(["ssh", "-i", secret_key_path, host, "-p", port, "ls", destination_dir], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #print(process.stdout)
    
    if process.returncode != 0:
        # 送信先フォルダが無ければ作成
        process = subprocess.run(["ssh", "-i", secret_key_path, host, "-p", port, "mkdir", destination_dir], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(process.stdout)

    # ファイル送信
    for file_path in files:
        if os.path.isfile(file_path):
            process = subprocess.run(["scp", "-P", port, "-i", secret_key_path, file_path, host + ":" + destination_dir], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            print("send", file_path, process.stdout)

    # 実行
    if files[0].endswith(".py"):
        process = subprocess.run(["ssh", "-i", secret_key_path, host, "-p", port, python_command, destination_dir + "/" + files[0]], encoding='utf-8', stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        print(process.stdout)

if __name__ == "__main__":
    main()

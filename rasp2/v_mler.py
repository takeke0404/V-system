import requests
import urllib
import json
import datetime
import time
import random
import os

import v_mysql
import v_liner
import v_scraper


class Manager:


    def __init__(self):
        mls_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mls.key")
        server_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "server.key")
        self.mls_url = None
        self.server_url = None

        if os.path.isfile(mls_key_path):
            with open(mls_key_path, "r") as key_file:
                self.mls_url = key_file.readline().splitlines()[0]
        else:
            raise Exception("MLer:" + mls_key_path + " does not exist.")

        if os.path.isfile(server_key_path):
            with open(server_key_path, "r") as key_file:
                self.server_url = key_file.readline().splitlines()[0]
        else:
            raise Exception("MLer:" + server_key_path + " does not exist.")

        self.database = v_mysql.Manager()
        self.liner = v_liner.Manager()


    def post(self, youtube_video_id):

        # 機械学習サーバに送信する。
        response = requests.post(urllib.parse.urljoin(self.mls_url, "post_url"), data = {"youtube_url" : "https://www.youtube.com/watch?v=" + youtube_video_id})

        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)

            if data[0] == "error":
                # analysis_status = 5
                self.update_analysis(youtube_video_id, 5)
            elif data[0] == "making":
                # analysis_status = 3
                self.update_analysis(youtube_video_id, 3)
            elif data[0] == "crowd":
                # analysis_status = 2
                pass
            else:
                # analysis_status = 4
                # v_server に送信する。
                response2 = requests.post(urllib.parse.urljoin(self.server_url, "api/video-analyzed"), data = response.text)

        else:
            raise Exception("MLer: Error in connecting to Machine Learning Server")


    def update_analysis(self, youtube_video_id, analysis_status, data_str = None):

        # データベースの更新
        self.database.connect()
        result = self.database.execute("SELECT id, title FROM video WHERE youtube_video_id = %s;", (youtube_video_id, ))
        if result:
            self.database.execute("UPDATE video SET analysis_status = %s, analysis_result = %s WHERE id = %s;", (analysis_status, data_str, result[0][0]))
        self.database.close()

        # 通知
        if result and analysis_status == 4 and data_str is not None:
            self.liner.send("解析が終了しました。\n" + result[0][1] + "\n" + youtube_video_id + "\n" + data_str)


    def analyze_next(self):

        # 解析すべき動画（チャットが存在すると確認されている）の取得
        self.database.connect()
        result = self.database.execute("SELECT youtube_video_id FROM video WHERE analysis_status = 2;")
        self.database.close()

        # print(result)
        if result:
            self.post(result[0][0])
            return

        # 解析すべき動画（チャットが存在すると確認されていない）の取得
        self.database.connect()
        result = self.database.execute("SELECT youtube_video_id, start FROM video WHERE analysis_status = 1;")
        self.database.close()

        # print(result)
        if result:
            for row in result:
                try:
                    data = v_scraper.youtube_video_ytInitialData(row[0])
                    chat = data["contents"]["twoColumnWatchNextResults"]["conversationBar"]
                    self.update_analysis(row[0], 2)
                    self.post(row[0])
                    print("POST", row[0])
                    break
                except Exception as e:
                    pass
                time.sleep(0.1 * random.randint(50, 150))

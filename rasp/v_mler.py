import requests
import json
import os

import v_mysql
import v_liner


class Manager:


    def __init__(self):
        mler_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mler.key")
        server_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "server.key")
        self.mler_url = None

        if os.path.isfile(mler_key_path):
            with open(mler_key_path, "r") as key_file:
                self.mler_url = key_file.readline().splitlines()[0]
        else:
            raise Exception("MLer:" + mler_key_path + " does not exist.")

        if os.path.isfile(server_key_path):
            with open(server_key_path, "r") as key_file:
                self.server_url = key_file.readline().splitlines()[0]
        else:
            raise Exception("MLer:" + server_key_path + " does not exist.")

        self.database = v_mysql.Manager()
        self.liner = v_liner.Manager()


    def post(self, youtube_video_id):

        # 機械学習サーバに送信する。
        response = requests.post(self.mler_url + "/post_url", data = {"youtube_url" : "https://www.youtube.com/watch?v=" + youtube_video_id})

        if response.status_code == requests.codes.ok:
            data = json.loads(response.text)
            analysis_status = 0
            data_str = None

            if data[0] == "error":
                analysis_status = 5
            elif data[0] == "making":
                analysis_status = 3
            elif data[0] == "crowd":
                analysis_status = 2
            else:
                analysis_status = 4
                data_str = json.dumps({"clip_times" : data[1:]})

            self.process_analysis_status(youtube_video_id, analysis_status, data_str)

        else:
            raise Exception("MLer: Error in connecting to Machine Learning Server")


    def process_analysis_status(self, youtube_video_id, analysis_status, data_str = None):

        # データベースの更新
        self.database.connect()
        result = self.database.execute("SELECT id, title FROM video WHERE youtube_video_id=%s;", (youtube_video_id, ))
        if result:
            self.database.execute("UPDATE video SET analysis_status=%s, analysis_result=%s WHERE id=%s;", (analysis_status, data_str, result[0][0]))
        self.database.close()

        # 通知
        if result and analysis_status == 4 and data_str is not None:
            self.liner.send("解析が終了しました。\n" + result[0][1] + "\n" + youtube_video_id + "\n" + data_str)


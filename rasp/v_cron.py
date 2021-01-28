from selenium import webdriver
import copy
import datetime
import time
import random
import traceback
import os
import sys

import v_mysql
import v_scraper
import v_liner
import v_mler


class Main:


    def __init__(self):

        try:

            # ログファイル出力先
            log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log")
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)
            if not os.path.isdir(log_dir):
                print(log_dir, "is not dir.")
                sys.exit()

            # モジュール読み込み
            liner = v_liner.Manager()
            self.mler = v_mler.Manager()
            self.database = v_mysql.Manager()

            # 通知文
            self.notification_end_video = ""
            self.notification_error = ""

            # vtuber を取得
            self.database.connect()
            sql_result_vtuber = self.database.execute("SELECT id, youtube_channel_id FROM vtuber;")
            self.database.close()

            # selenium driver 起動
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            options.add_argument('--disable-gpu')
            driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options = options)

            # 変数の用意
            searched_video_ids = set()
            self.week_after = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks = 1)

            for vtuber_id, youtube_channel_id in sql_result_vtuber:
                # YouTube チャンネル
                print("YouTube Channel:", vtuber_id, youtube_channel_id)

                # 調べる
                youtube_video_ids = v_scraper.youtube_channel(driver, youtube_channel_id)

                self.wait_a_minute()

                for youtube_video_id in youtube_video_ids:
                    # YouTube 動画

                    # 動画に関する処理を行う
                    video_id = self.process_video(youtube_video_id, vtuber_id)

                    # 新規動画
                    if video_id is not None:
                        searched_video_ids.add(youtube_video_id)

                    self.wait_a_minute()

            driver.quit()

            # 調べるべき動画
            self.database.connect()
            sql_result_video = self.database.execute("SELECT id, vtuber_id, youtube_video_id FROM video WHERE status=1 OR status=2;")
            self.database.close()

            for video_id, vtuber_id, youtube_video_id in sql_result_video:
                if video_id not in searched_video_ids:
                    # 先程調べていなかった動画

                    # 動画に関する処理を行う
                    self.process_video(youtube_video_id, vtuber_id)

                    self.wait_a_minute()

            # LINE への通知
            line_message = ""
            if self.notification_end_video:
                line_message += "配信が終了しました。\n" + self.notification_end_video
            if self.notification_error:
                line_message += "エラーが発生しました。\n" + self.notification_error
            if line_message:
                liner.send(line_message)

        except Exception as e:
            print(traceback.format_exc())

            now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")

            # LINE
            try:
                liner.send("ERROR: v_cron.py\n" + now_str + "(UTC)\n" + traceback.format_exc())
            except Exception as e:
                pass

            # ログファイル
            try:
                log_path = os.path.join(log_dir, now_str + ".log")
                with open(log_path, mode = "w", encoding = "utf_8") as log_file:
                    log_file.write("ERROR: v_cron.py\n" + now_str + "(UTC)\n" + traceback.format_exc())
            except Exception as e:
                pass


    def process_video(self, youtube_video_id, vtuber_id):
        print("YouTube Video:", youtube_video_id)
        video_id = None
        video_end = False

        # 調べる
        status, title, start_datetime, end_datetime = v_scraper.youtube_video(youtube_video_id)

        # 日時を文字列に
        start_str = None if start_datetime is None else start_datetime.isoformat()
        end_str = None if end_datetime is None else end_datetime.isoformat()

        self.database.connect()

        # データベースに存在するか確認する
        result = self.database.execute("SELECT id, notified FROM video WHERE youtube_video_id=%s;", (youtube_video_id, ))
        if result:
            # データベースに存在する
            video_id = result[0][0]
            notified = result[0][1]

            if status == 3 and not notified & 64:
                # 配信が終了した
                notified = notified | 64
                video_end = True

            # データベース更新
            self.database.execute("UPDATE video SET status=%s, title=%s, start=%s, end=%s, notified=%s WHERE id=%s;", (status, title, start_str, end_str, notified, video_id))
        else:
            # データベースに存在しない
            if start_datetime is not None and start_datetime < self.week_after:

                if status == 3:
                    # 配信が終了していた
                    notified = 64
                    video_end = True
                else:
                    notified = 0

                # データベース追加
                self.database.execute("INSERT INTO video (vtuber_id, status, title, youtube_video_id, start, end, notified) VALUES (%s, %s, %s, %s, %s, %s, %s);", (vtuber_id, status, title, youtube_video_id, start_str, end_str, notified))
                video_id = self.database.execute("SELECT LAST_INSERT_ID();")[0][0]

        self.database.close()

        if video_end:
            self.process_end_video(title, youtube_video_id)

        return video_id


    def process_end_video(self, title, youtube_video_id):
        self.notification_end_video += title + "\nhttps://www.youtube.com/watch?v=" + youtube_video_id + "\n\n"

        try:
            self.mler.post(youtube_video_id)
        except Exception as e:
            self.notification_error += "機械学習サーバとの通信に失敗しました。\n" + traceback.format_exc() + "\n\n"


    def wait_a_minute(self):
        """１分待つわけじゃないよ。"""
        time.sleep(0.1 * random.randint(20, 40))


if __name__ == "__main__":
    Main()


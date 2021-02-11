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


    def __init__(self, level):

        try:

            self.level = level

            # ログファイル出力先
            log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log")
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)

            # モジュール読み込み
            self.liner = v_liner.Manager()
            self.mler = v_mler.Manager()
            self.database = v_mysql.Manager()

            # 通知文
            self.notification_end_video = ""
            self.notification_error = ""

            # selenium driver 起動
            driver = None
            if self.level == 1:
                options = webdriver.ChromeOptions()
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')
                driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options = options)

            # vtuber を取得
            self.database.connect()
            sql_result_vtuber = self.database.execute("SELECT id, youtube_channel_id, editor_id FROM vtuber WHERE editor_id>=1;")
            self.database.close()

            # 変数の用意
            searched_video_ids = set()
            self.week_after = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks = 1)

            for vtuber_id, youtube_channel_id, editor_id in sql_result_vtuber:
                # YouTube チャンネル
                print("YouTube Channel:", vtuber_id, youtube_channel_id)
                will_analyze = True if editor_id >= 2 else False

                # 調べる
                youtube_video_ids = set()
                if self.level == 1:
                    youtube_video_ids = v_scraper.youtube_channel(driver, youtube_channel_id)

                # ライブ配信埋め込みURL
                youtube_video_id = v_scraper.youtube_embedded_live(youtube_channel_id)
                if youtube_video_id is not None:
                    youtube_video_ids.add(youtube_video_id)

                self.wait_a_minute()

                for youtube_video_id in youtube_video_ids:
                    # YouTube 動画

                    # 動画に関する処理を行う
                    video_id = self.process_video(youtube_video_id, vtuber_id, will_analyze)

                    if video_id is not None:
                        # データベースに存在する動画
                        searched_video_ids.add(video_id)

                    self.wait_a_minute()

            # selenium driver 終了
            if self.level == 1:
                driver.quit()

            # 調べるべき動画
            self.database.connect()
            sql_result_video = self.database.execute(
                "SELECT video.id, video.vtuber_id, video.youtube_video_id, vtuber.editor_id "
                "FROM video INNER JOIN vtuber ON video.vtuber_id=vtuber.id "
                "WHERE (video.status=1 OR video.status=2) AND vtuber.editor_id>=1;")
            self.database.close()

            for video_id, vtuber_id, youtube_video_id, editor_id in sql_result_video:
                if video_id not in searched_video_ids:
                    # 先程調べていなかった動画

                    # 動画に関する処理を行う
                    will_analyze = True if editor_id >= 2 else False
                    self.process_video(youtube_video_id, vtuber_id, will_analyze)

                    self.wait_a_minute()

            # 未解析動画
            try:
                self.mler.analyze_next()
            except Exception as e:
                self.notification_error += "機械学習サーバに解析を依頼できません。\n" + traceback.format_exc() + "\n\n"

            # 通知する
            self.notify(self.liner)

        except Exception as e:
            self.report_error(traceback.format_exc(), log_dir, self.liner)

    def process_video(self, youtube_video_id, vtuber_id, will_analyze):
        print("YouTube Video:", youtube_video_id)
        video_id = None

        # 調べる
        status, title, start_datetime, end_datetime, youtube_channel_ids, exists_chat = v_scraper.youtube_video(youtube_video_id)

        # 日時を文字列に
        start_str = None if start_datetime is None else start_datetime.isoformat()
        end_str = None if end_datetime is None else end_datetime.isoformat()

        self.database.connect()

        # コラボを確認する
        collaboration_vtuber_ids_string = None
        if youtube_channel_ids:
            result = self.database.execute("SELECT id FROM vtuber WHERE youtube_channel_id=%s" + (" OR youtube_channel_id=%s" * (len(youtube_channel_ids) - 1)) + ";", youtube_channel_ids)
            collaboration_vtuber_ids_string = ",".join([str(row[0]) for row in result if row[0] != vtuber_id].sort())

        # データベースに存在するか確認する
        result = self.database.execute("SELECT id, notified, analysis_status FROM video WHERE youtube_video_id=%s;", (youtube_video_id, ))
        if result:
            # データベースに存在する
            video_id = result[0][0]
            notified = result[0][1]
            analysis_status = result[0][2]

            if status == 3:
                # 配信が終了した

                if not notified & 64:
                    # 通知がまだ
                    notified = notified | 64
                    self.add_end_video(title, youtube_video_id, collaboration_vtuber_ids_string)

                if will_analyze and analysis_status < 2:
                    # 解析を予定する
                    analysis_status = 2

            # データベース更新
            self.database.execute("UPDATE video SET status=%s, title=%s, start=%s, end=%s, collaboration_vtuber=%s, notified=%s, analysis_status=%s WHERE id=%s;", (status, title, start_str, end_str, collaboration_vtuber_ids_string, notified, analysis_status, video_id))
        else:
            # データベースに存在しない
            if start_datetime is not None and start_datetime < self.week_after:
                # 配信動画 and 一週間以内に配信する動画

                notified = 0
                analysis_status = 0

                if status == 3:
                    # 配信が終了していた

                    # 通知
                    notified = 64
                    self.add_end_video(title, youtube_video_id, collaboration_vtuber_ids_string)

                    if will_analyze:
                        # 解析を予定する
                        analysis_status = 2

                # データベース追加
                self.database.execute("INSERT INTO video (vtuber_id, status, title, youtube_video_id, start, end, collaboration_vtuber, notified, analysis_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);", (vtuber_id, status, title, youtube_video_id, start_str, end_str, collaboration_vtuber_ids_string, notified, analysis_status))
                video_id = self.database.execute("SELECT LAST_INSERT_ID();")[0][0]

        self.database.close()

        return video_id


    def add_end_video(self, title, youtube_video_id, collaboration_vtuber_ids_string):
        self.notification_end_video += title + "\nhttps://www.youtube.com/watch?v=" + youtube_video_id + "\n"
        if collaboration_vtuber_ids_string is not None:
            self.notification_end_video += "コラボ： " + collaboration_vtuber_ids_string + "\n"
        self.notification_end_video += "\n"


    def notify(self, liner):
        # LINE への通知
        line_message = ""
        if self.notification_end_video:
            line_message += "配信が終了しました。\n" + self.notification_end_video
        if self.notification_error:
            line_message += "エラーが発生しました。\n" + self.notification_error
        if line_message:
            liner.send(line_message)


    def wait_a_minute(self):
        """１分待つわけじゃないよ。"""
        time.sleep(0.1 * random.randint(20, 40))


    def report_error(self, trace, log_dir, liner):
        print(trace)

        now_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y_%m_%d_%H_%M_%S")

        # ログファイル
        try:
            log_path = os.path.join(log_dir, now_str + ".log")
            with open(log_path, mode = "w", encoding = "utf_8") as log_file:
                log_file.write("ERROR: v_cron.py\n" + now_str + "(UTC)\n" + trace)
        except Exception as e:
            pass

        # LINE
        try:
            liner.send("ERROR: v_cron.py\n" + now_str + "(UTC)\n" + trace)
        except Exception as e:
            pass


if __name__ == "__main__":
    level = sys.argv[1] if len(sys.argv) > 1 else 1
    Main(level)

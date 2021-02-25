import datetime
import time
import re
import random
import traceback
import os

import v_scraper
import v_mysql
import v_liner


class Main:

    def __init__(self):

        try:

            # ログファイル出力先
            log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), "log")
            if not os.path.exists(log_dir):
                os.mkdir(log_dir)

            # モジュール読み込み
            self.database = v_mysql.Manager()
            self.liner = v_liner.Manager()

            # 開始
            print("v_cron2.py", datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"), "(UTC)")
            self.notification_end_video = ""

            # vtuber を取得
            self.database.connect()
            sql_result_vtuber = self.database.execute(
                "SELECT id, youtube_channel_id, youtube_api_key, editor_id "
                "FROM vtuber "
                "WHERE editor_id >= 1 AND youtube_channel_id IS NOT NULL AND youtube_api_key IS NOT NULL;")
            self.database.close()

            # vtuber ループ
            for vtuber_id, youtube_channel_id, youtube_api_key, editor_id in sql_result_vtuber:
                print("YouTube Channel:", vtuber_id, youtube_channel_id)
                self.wait_a_minute()

                # 動画を取得
                self.database.connect()
                sql_result_video = self.database.execute(
                    "SELECT id, youtube_video_id, collaboration_vtuber, notified, analysis_status "
                    "FROM video "
                    "WHERE vtuber_id = %s AND (status = 1 OR status = 2);", (vtuber_id, ))
                self.database.close()

                if sql_result_video:
                    # 動画情報を取得
                    videos = v_scraper.youtube_video(",".join([str(row[1]) for row in sql_result_video]), youtube_api_key)

                    # 動画ループ
                    self.database.connect()
                    for youtube_video_id, status, title, start_datetime, end_datetime in videos:

                        # データベース情報と連結
                        row = None
                        for i in range(len(sql_result_video)):
                            if sql_result_video[i][1] == youtube_video_id:
                                row = sql_result_video.pop(i)
                                break
                        if row:
                            video_id = row[0]
                            collaboration_vtuber = row[2]
                            notified = row[3]
                            analysis_status = row[4]
                        else:
                            continue

                        print("YouTube Video:", youtube_video_id)

                        # 日時を文字列に
                        start_str = None if start_datetime is None else start_datetime.isoformat()
                        end_str = None if end_datetime is None else end_datetime.isoformat()

                        if status == 3:
                            # 配信が終了した

                            if not notified & 64:
                                # 通知がまだ
                                notified = notified | 64
                                self.notification_end_video += title + "\nhttps://www.youtube.com/watch?v=" + youtube_video_id + "\n"
                                if collaboration_vtuber is not None:
                                    self.notification_end_video += "コラボ： " + collaboration_vtuber + "\n"
                                self.notification_end_video += "\n"

                            if editor_id > 1 and analysis_status < 1:
                                # 解析を予定する
                                analysis_status = 1

                        # データベース更新
                        self.database.execute(
                            "UPDATE video SET status = %s, title = %s, start = %s, end = %s, notified = %s, analysis_status = %s WHERE id = %s;",
                            (status, title, start_str, end_str, notified, analysis_status, video_id))

                    # 存在しない動画
                    for row in sql_result_video:
                        print("YouTube Video DELETED:", row[1])
                        self.database.execute("UPDATE video SET status = 6 WHERE id = %s;", (row[0], ))

                    self.database.close()

            if self.notification_end_video:
                self.liner.send("配信が終了しました。\n" + self.notification_end_video)

        except Exception as e:
            self.report_error(traceback.format_exc(), log_dir, self.liner)


    def wait_a_minute(self):
        """１分待つわけじゃないよ。"""
        time.sleep(0.1 * random.randint(30, 70))


    def report_error(self, trace, log_dir, liner):
        print(trace)

        now_datetime = datetime.datetime.now(datetime.timezone.utc)

        # ログファイル
        try:
            log_path = os.path.join(log_dir, "v_cron2_" + now_datetime.strftime("%Y_%m_%d_%H_%M_%S") + ".log")
            with open(log_path, mode = "w", encoding = "utf_8") as log_file:
                log_file.write("ERROR: v_cron2.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass

        # LINE
        try:
            self.liner = v_liner.Manager()
            liner.send("ERROR: v_cron2.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass


if __name__ == "__main__":
    Main()

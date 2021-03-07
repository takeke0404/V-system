import datetime
import time
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

            # YouTube Data API Key 読み込み
            youtube_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "youtube.key")
            if os.path.isfile(youtube_key_path):
                with open(youtube_key_path, "r") as key_file:
                    self.youtube_key = key_file.readline().splitlines()[0]
            else:
                raise Exception(youtube_key_path + " does not exist.")

            # モジュール読み込み
            self.database = v_mysql.Manager()
            self.liner = v_liner.Manager()

            # 開始
            print("v_cron2.py", datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"), "(UTC)")
            self.notification_end_video = ""

            # 動画を取得
            self.database.connect()
            sql_result_video = self.database.execute(
                "SELECT video.id, video.youtube_video_id, video.collaboration_vtuber, video.notified, video.analysis_status, vtuber.editor_id "
                "FROM video INNER JOIN vtuber ON video.vtuber_id = vtuber.id "
                "WHERE (video.status = 1 OR video.status = 2) AND vtuber.editor_id >= 1 AND vtuber.youtube_channel_id IS NOT NULL;")
            self.database.close()

            if sql_result_video:
                searched_video_id_set = set()
                # 動画50個ループ
                for i in range(0, len(sql_result_video), 50):

                    # 動画情報を取得
                    self.wait_a_minute()
                    videos = v_scraper.youtube_video(",".join([str(row[1]) for row in sql_result_video[i : i + 50]]), self.youtube_key)

                    # 動画ループ
                    self.database.connect()
                    for youtube_video_id, status, title, start_datetime, end_datetime in videos:

                        # データベース情報と連結
                        row = None
                        for j in range(len(sql_result_video[i : i + 50])):
                            if sql_result_video[i : i + 50][j][1] == youtube_video_id:
                                row = sql_result_video[i : i + 50][j]
                                break
                        if row:
                            video_id = row[0]
                            collaboration_vtuber = row[2]
                            notified = row[3]
                            analysis_status = row[4]
                            editor_id = row[5]
                        else:
                            continue

                        print("YouTube Video:", youtube_video_id)
                        searched_video_id_set.add(video_id)

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

                    self.database.close()

                # 存在しない動画
                self.database.connect()
                for row in sql_result_video:
                    if row[0] not in searched_video_id_set:
                        print("YouTube Video DELETED:", row[1])
                        self.database.execute("UPDATE video SET status = 6 WHERE id = %s;", (row[0], ))
                self.database.close()

            if self.notification_end_video:
                self.liner.send("配信が終了しました。\n" + self.notification_end_video)

        except Exception as e:
            self.report_error(traceback.format_exc(), log_dir, self.liner)


    def wait_a_minute(self):
        """１分待つわけじゃないよ。"""
        time.sleep(0.1 * random.randint(50, 150))


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

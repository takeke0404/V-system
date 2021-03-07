import datetime
import time
import random
import urllib
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
            print("v_cron1.py", datetime.datetime.now(datetime.timezone.utc).strftime("%Y/%m/%d %H:%M:%S"), "(UTC)")

            # vtuber を取得
            self.database.connect()
            sql_result_vtuber = self.database.execute(
                "SELECT id, youtube_channel_id "
                "FROM vtuber "
                "WHERE editor_id >= 1 AND youtube_channel_id IS NOT NULL;")
            self.database.close()

            # vtuber ループ
            youtube_video_id_dict = dict()
            for vtuber_id, youtube_channel_id in sql_result_vtuber:
                print("YouTube Channel:", vtuber_id, youtube_channel_id)

                # 動画を取得
                self.wait_a_minute()
                youtube_video_id_set = v_scraper.youtube_channel(youtube_channel_id)

                if youtube_video_id_set:
                    # データベースに存在するか確認
                    self.database.connect()
                    sql_result_video = self.database.execute(
                        "SELECT youtube_video_id FROM video WHERE youtube_video_id = %s" + (" OR youtube_video_id = %s" * (len(youtube_video_id_set) - 1)) + ";",
                        list(youtube_video_id_set))
                    self.database.close()

                    # データベースに存在する動画を除外
                    for row in sql_result_video:
                        youtube_video_id_set.discard(row[0])

                if youtube_video_id_set:
                    # vtuber との対応表（辞書）を作成
                    for youtube_video_id in youtube_video_id_set:
                        youtube_video_id_dict[youtube_video_id] = vtuber_id

            # 動画50個ループ
            youtube_video_id_list = list(youtube_video_id_dict.keys())
            for i in range(0, len(youtube_video_id_list), 50):
                print("YouTube Videos:", youtube_video_id_list[i : i + 50])

                # 動画情報を取得
                self.wait_a_minute()
                videos = v_scraper.youtube_video(",".join(youtube_video_id_list[i : i + 50]), self.youtube_key)

                # 動画ループ
                for youtube_video_id, status, title, start_datetime, end_datetime in videos:
                    vtuber_id = youtube_video_id_dict[youtube_video_id]

                    # コラボを確認する
                    collaboration_vtuber_id_join = None
                    self.wait_a_minute()
                    data = v_scraper.youtube_video_ytInitialData(youtube_video_id)
                    self.database.connect()
                    if data is not None:
                        youtube_channel_id_set = set()
                        try:
                            descriptions = data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][1]["videoSecondaryInfoRenderer"]["description"]["runs"]

                            for description in descriptions:
                                try:
                                    # YouTube チャンネルのURLを検出
                                    link = description["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]
                                    if link["webPageType"] == "WEB_PAGE_TYPE_CHANNEL":
                                        youtube_channel_id_set.add(link["url"].split("/")[2])
                                    elif link["webPageType"] == "WEB_PAGE_TYPE_UNKNOWN":
                                        url_parse = urllib.parse.urlparse(link["url"])
                                        if (url_parse.netloc == "www.youtube.com" or url_parse.netloc == "") and url_parse.path.startswith("/channel/"):
                                            youtube_channel_id_set.add(url_parse.path.split("/")[2])
                                except Exception as e:
                                    pass

                        except Exception as e:
                            pass

                        if youtube_channel_id_set:
                            # データベースに存在する vtuber か確認
                            result = self.database.execute(
                                "SELECT id FROM vtuber WHERE youtube_channel_id = %s" + (" OR youtube_channel_id = %s" * (len(youtube_channel_id_set) - 1)) + ";",
                                list(youtube_channel_id_set))

                            # 配信者のチャンネルを除いたリスト化
                            collaboration_vtubers = [row[0] for row in result if row[0] != vtuber_id]

                            # チャンネルID連結文字列化
                            if collaboration_vtubers:
                                collaboration_vtubers.sort()
                                collaboration_vtuber_id_join = ",".join([str(row) for row in collaboration_vtubers])

                    # 日時を文字列に
                    start_str = None if start_datetime is None else start_datetime.isoformat()
                    end_str = None if end_datetime is None else end_datetime.isoformat()

                    # INSERT
                    print("INSERT", youtube_video_id)
                    self.database.execute(
                        "INSERT INTO video (vtuber_id, status, title, youtube_video_id, start, end, collaboration_vtuber) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                        (vtuber_id, 1, title, youtube_video_id, start_str, end_str, collaboration_vtuber_id_join))

                    self.database.close()

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
            log_path = os.path.join(log_dir, "v_cron1_" + now_datetime.strftime("%Y_%m_%d_%H_%M_%S") + ".log")
            with open(log_path, mode = "w", encoding = "utf_8") as log_file:
                log_file.write("ERROR: v_cron1.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass

        # LINE
        try:
            self.liner = v_liner.Manager()
            liner.send("ERROR: v_cron1.py " + now_datetime.strftime("%Y/%m/%d %H:%M:%S") + " (UTC)\n" + trace)
        except Exception as e:
            pass


if __name__ == "__main__":
    Main()

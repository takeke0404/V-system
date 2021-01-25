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


def main():

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
        database = v_mysql.Manager()

        # 始まりのお知らせ
        liner.send("v_cron を起動します。")

        # vtuber を取得
        database.connect()
        sql_result_vtuber = database.execute("SELECT id, youtube_channel_id FROM vtuber;")
        database.close()

        # selenium driver 起動
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options = options)

        # 変数の用意
        searched_video_ids = set()
        week_after = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks = 1)

        for vtuber_id, youtube_channel_id in sql_result_vtuber:
            # YouTube チャンネル
            print("YouTube Channel:", vtuber_id, youtube_channel_id)

            # 
            youtube_video_ids = v_scraper.youtube_channel(driver, youtube_channel_id)

            wait_a_minute()

            for youtube_video_id in youtube_video_ids:
                # YouTube 動画
                print("YouTube Video:", youtube_video_id)

                # 
                video_id = process_video(database, week_after, youtube_video_id, vtuber_id)
                if video_id is not None:
                    searched_video_ids.add(youtube_video_id)

                wait_a_minute()

        driver.quit()

        # 調べるべき動画
        database.connect()
        sql_result_video = database.execute("SELECT id, vtuber_id, youtube_video_id FROM video WHERE status=1 OR status=2;")
        database.close()

        for video_id, vtuber_id, youtube_video_id in sql_result_video:
            if video_id not in searched_video_ids:
                # 先程調べていなかった動画
                print("YouTube Video:", youtube_video_id)

                process_video(database, week_after, youtube_video_id, vtuber_id)

                wait_a_minute()

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


def process_video(database, week_after, youtube_video_id, vtuber_id):

    video_id = None

    # 
    status, title, start_datetime, end_datetime = v_scraper.youtube_video(youtube_video_id)

    # 日時を文字列に
    start_str = None if start_datetime is None else start_datetime.isoformat()
    end_str = None if end_datetime is None else end_datetime.isoformat()

    database.connect()

    # データベースに存在するか確認する
    result = database.execute("SELECT id FROM video WHERE youtube_video_id=%s;", (youtube_video_id, ))
    if result:
        # データベースに存在する
        video_id = result[0][0]
        database.execute("UPDATE video SET status=%s, title=%s, start=%s, end=%s WHERE id=%s;", (status, title, start_str, end_str, video_id))
    else:
        # データベースに存在しない
        if start_datetime is not None and start_datetime < week_after:
            database.execute("INSERT INTO video (vtuber_id, status, title, youtube_video_id, start, end) VALUES (%s, %s, %s, %s, %s, %s);", (vtuber_id, status, title, youtube_video_id, start_str, end_str))
            video_id = database.execute("SELECT LAST_INSERT_ID();")[0][0]

    database.close()

    return video_id


def wait_a_minute():
    """１分待つわけじゃないよ。"""
    time.sleep(0.1 * random.randint(20, 40))


if __name__ == "__main__":
    main()


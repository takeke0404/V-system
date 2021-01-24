from selenium import webdriver
import datetime
import time
import random
import traceback
import os
import sys

import v_mysql
import v_scraper


def main():

    # ログファイル出力先
    log_dir_name = "log"
    log_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), log_dir_name)
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)
    if not os.path.isdir(log_dir):
        print(log_dir, "is not dir.")
        sys.exit()

    try:
        database = v_mysql.Manager()

        # vtuber を取得
        database.connect()
        sql_result_1 = database.execute("SELECT id, youtube_channel_id FROM vtuber;")
        sql_result_2 = database.execute("SELECT id, youtube_video_id FROM video;")
        database.close()

        # selenium driver 起動
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(executable_path="/usr/lib/chromium-browser/chromedriver", options = options)

        # 
        insert_videos = [] # (vtuber_id, status, title, youtube_video_id, start, end)
        update_videos = [] # (status, title, start, end, id)
        week_after = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(weeks = 1)

        for vtuber_id, youtube_channel_id in sql_result_1:
            # YouTube チャンネル
            print("YouTube Channel:", vtuber_id, youtube_channel_id)

            youtube_video_ids = v_scraper.youtube_channel(driver, youtube_channel_id)

            wait_a_minute()

            for youtube_video_id in youtube_video_ids:
                # YouTube 動画
                print("YouTube Video:", youtube_video_id)

                # データベースに存在するか確認
                video_id = None
                for v_id, yt_v_id in sql_result_2:
                    if youtube_video_id == yt_v_id:
                        video_id = v_id

                status, title, start, end = v_scraper.youtube_video(youtube_video_id)
                start_datetime = None if start is None else start.isoformat()
                end_datetime = None if end is None else end.isoformat()

                if video_id is None:
                    # データベースに存在しない
                    if start is not None and start < week_after:
                        insert_videos.append((vtuber_id, status, title, youtube_video_id, start_datetime, end_datetime))
                else:
                    # データベースに存在する
                    update_videos.append((status, title, start_datetime, end_datetime, video_id))

                wait_a_minute()

        driver.quit()

        database.connect()
        if insert_videos:
            print(insert_videos)
            result = database.executemany("INSERT INTO video (vtuber_id, status, title, youtube_video_id, start, end) VALUES (%s, %s, %s, %s, %s, %s);", insert_videos)
        if update_videos:
            print(insert_videos)
            result = database.executemany("UPDATE video SET status=%s, title=%s, start=%s, end=%s WHERE id=%s;", update_videos)
        database.close()

    except Exception as e:
        print(traceback.format_exc())


def wait_a_minute():
    """１分待つわけじゃないよ。"""
    time.sleep(0.1 * random.randint(20, 40))


if __name__ == "__main__":
    main()


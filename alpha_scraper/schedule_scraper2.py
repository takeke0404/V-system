import csv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
import requests
from bs4 import BeautifulSoup
import re
import json
import time
import datetime
import os
import sys

"""
Selenium を利用してライブ配信とその予定の時刻を取得します。
"""

youtube_channels_path = "youtube_channels.csv"

chrome_version = "87"

TYPE_SCHEDULE = "schedule"
TYPE_LIVE = "live"

def main():
    
    youtube_channels = load_youtube_channels(youtube_channels_path)
    print(youtube_channels)

    # Chrome 起動
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(executable_path = os.path.join("chromedriver", "chromedriver" + chrome_version), options = options)

    # YouTube チャンネルを調べる。
    youtube_videos = explore_youtube_channels(driver, youtube_channels)

    print(youtube_videos)

    for video_url in youtube_videos[TYPE_SCHEDULE] + youtube_videos[TYPE_LIVE]:
        video_info = investigate_youtube_video(video_url)


    #time.sleep(1)
    driver.quit()

def load_youtube_channels(path):
    if os.path.isfile(path):
        youtube_channels = []
        with open(path, "r") as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                if len(line) > 0:
                    youtube_channels.append(line[0])
        return youtube_channels
    else:
        print(path, "is not exist.")
        sys.exit()

def explore_youtube_channels(driver, youtube_channels):
    """YouTube チャンネル巡回"""

    youtube_videos = {TYPE_SCHEDULE : [], TYPE_LIVE : []}

    for youtube_channel in youtube_channels:

        print(youtube_channel)

        # YouTube チャンネルページ
        driver.get(youtube_channel)

        item_sections = driver.find_elements_by_tag_name("ytd-item-section-renderer")
        for item_section in item_sections:
            # 動画横一列分（セクション）
            #print(item_section.text)

            try:
                # セクションのタイトル
                section_title = item_section.find_element_by_css_selector("div#title-container div#title-text")
                #print(section_title.text)
                section_title_link = section_title.find_element_by_tag_name("a")
                section_title_link_url = section_title_link.get_attribute("href")
                #print(section_title_link_url)

                section_type = None
                if "live_view=502" in section_title_link_url:
                    # 今後のライブストリーム
                    section_type = TYPE_SCHEDULE

                elif "live_view=501" in section_title_link_url:
                    # ライブ配信中
                    section_type = TYPE_LIVE

                # セクションの中身
                if section_type:
                    #print(section_type)

                    grid_videos = item_section.find_elements_by_tag_name("ytd-grid-video-renderer")
                    if grid_videos:
                        # 動画が横に並んでる

                        for grid_video in grid_videos:
                            #print(grid_video.text.splitlines())

                            video_link = grid_video.find_element_by_css_selector("a#video-title")
                            video_link_url = video_link.get_attribute("href")

                            youtube_videos[section_type].append(video_link_url)

                            print(section_type, video_link_url, video_link.get_attribute("title"))
                    else:
                        # 横幅いっぱいに一つの動画

                        video = item_section.find_element_by_tag_name("ytd-video-renderer")
                        video_link = video.find_element_by_css_selector("a#video-title")
                        video_link_url = video_link.get_attribute("href")

                        youtube_videos[section_type].append(video_link_url)

                        print(section_type, video_link_url, video_link.get_attribute("title"))

            except NoSuchElementException:
                pass

        print()
        #break

    return youtube_videos

def investigate_youtube_video(video_url):
    web_page = requests.get(video_url)

    #print("startDate" in web_page.text)
    #print(web_page.text.count("startDate"))
    #a = web_page.text.find("startDate")
    #print(web_page.text[a-100:a+100])
    #print("startTime" in web_page.text)
    #print(web_page.text.count("startTime"))
    #for a in [m.start() for m in re.finditer("date", web_page.text, flags=re.IGNORECASE)]:
    #    print(web_page.text[a-100:a+100])
    #print(web_page.text.count("2021"))

    title_text = None
    start_date = None
    start_datetime = None
    end_date = None
    end_datetime = None
    islive = None
    
    soup = BeautifulSoup(web_page.text, "html.parser")

    title = soup.find("title")
    if title:
        title_text = title.get_text()

    title_meta = soup.find("meta", {"name" : "title"})
    if title_meta:
        title_text = title_meta.get("content")

    start_meta = soup.find("meta", {"itemprop" : "startDate"})
    if start_meta:
        start_date = start_meta.get("content")
        start_datetime = datetime.datetime.fromisoformat(start_date)

    end_meta = soup.find("meta", {"itemprop" : "endDate"})
    if end_meta:
        end_date = end_meta.get("content")
        end_datetime = datetime.datetime.fromisoformat(end_date)

    islive_meta = soup.find("meta", {"itemprop" : "isLiveBroadcast"})
    if islive_meta:
        islive = islive_meta.get("content")

    print(video_url)
    print("", title_text)
    print("", start_date, "-", end_date)
    print("", start_datetime, "-", end_datetime)
    print("", "isLive", islive)

    metas = soup.find_all("meta")
    for meta in metas:
        if meta.get("property"):
            if "og:video:tag" in meta.get("property"):
                continue
        
        #print(meta)

    #print("", "scheduledStartTime", "scheduledStartTime" in web_page.text)

    #for a in [m.start() for m in re.finditer("scheduledStartTime", web_page.text, flags=re.IGNORECASE)]:
    #    #print(web_page.text[a-1000:a+1000])
    #    t = ""
    #    for s in soup.find_all("script"):
    #        if s.string:
    #            #print(s.string)
    #            t += "" + s.string + "\n"

    #print("", "playabilityStatus" in web_page.text)
    for a in [m.start() for m in re.finditer("\"status\":", web_page.text, flags=re.IGNORECASE)]:
        print(web_page.text[a:a+100])
    
    #print("", "LIVE_STREAM_OFFLINE" in web_page.text)

    for s in soup.find_all("script"):
        script_content = s.string
        if script_content:
            #print(script_content)

            #script_content2 = script_content.replace("\\\"", "")
            if "\"scheduledStartTime\":" in script_content:
                print("scheduledStartTime")

            if "\"status\":\"LIVE_STREAM_OFFLINE\"," in script_content:
                print("LIVE_STREAM_OFFLINE")

            if "\"status\":\"UNPLAYABLE\"," in script_content:
                print("UNPLAYABLE")
            #json_keys = re.findall("\".*?\".*?:.*?\".*?\"", script_content2, re.DOTALL)
            #for t in json_keys:
            #    if "scheduledStartTime" in t:
            #        print(json_keys)
            #        print("scheduledStartTime")

    #with open("tmp.txt", mode = "w", encoding = "utf_8") as f:
    #    f.write(web_page.text)

    print()
    return (video_url, title_text, start_date, end_date)

if __name__ == "__main__":
    #main()
    if True:
        # 消去された配信
        investigate_youtube_video("https://www.youtube.com/watch?v=g4tCXx7tBWs")
        # 配信済み
        investigate_youtube_video("https://www.youtube.com/watch?v=G7IBLfDovwU")
        # 配信ではない動画
        investigate_youtube_video("https://www.youtube.com/watch?v=WQYN2P3E06s")
        # 配信予定
        investigate_youtube_video("https://www.youtube.com/watch?v=khJugsohbuY")
        # メンバー限定
        investigate_youtube_video("https://www.youtube.com/watch?v=FLIIJlfguiY")

        investigate_youtube_video("https://www.youtube.com/watch?v=bmUCzUZllSI")

        investigate_youtube_video("https://www.youtube.com/watch?v=w303bMEvLtU")

        investigate_youtube_video("https://www.youtube.com/watch?v=xP89_B0pBYw")

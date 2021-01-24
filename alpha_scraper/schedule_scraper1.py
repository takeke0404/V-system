import csv
import requests
import re
from bs4 import BeautifulSoup
from apiclient.discovery import build
import os
import sys

"""
ライブ配信の埋め込みURLから、YouTube API で情報を取得します。
"""

youtube_data_api_key_path = "youtube_data_api_key.txt"
youtube_data_api_key = ""

youtube_channels_path = "youtube_channels.csv"
youtube_channels = []

YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

def main():
    
    load_youtube_data_api_key()
    print(youtube_data_api_key)

    load_youtube_channels()
    print(youtube_channels)

    # href="https:// ... watch?v=******"
    video_id_pattern = re.compile(r"watch\?v=(.*?)\"")

    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, developerKey = youtube_data_api_key)

    for youtube_channel in youtube_channels:

        print(youtube_channel)

        # ライブ配信埋め込みURL
        url = "https://www.youtube.com/embed/live_stream?channel=" + youtube_channel.split("/")[-1]
        print(url)
        
        # Web ページ取得
        web_page = requests.get(url)
        #print("watch?v=" in web_page.text)

        #with open("tmp.txt", mode = "w", encoding = "utf_8") as f:
        #    f.write(web_page.text)

        
        # video ID 探索
        search_result = video_id_pattern.search(web_page.text)
        if search_result:
            video_id = search_result.groups()[0]
            print("video_id", video_id)
            #response = youtube.videos().list(part = 'snippet', id = video_id).execute()
            #print(response["items"][0]["snippet"]["title"])

        # video ID 探索 2
        soup = BeautifulSoup(web_page.text, "html.parser")
        link = soup.find("a")
        print(link.get("href").split("watch?v=")[-1])

        print()
        break

def load_youtube_data_api_key():
    global youtube_data_api_key
    if os.path.isfile(youtube_data_api_key_path):
        with open(youtube_data_api_key_path, "r") as key_file:
            youtube_data_api_key = key_file.readline().splitlines()[0]
    else:
        print(youtube_data_api_key_path, "is not exist.")
        sys.exit()

def load_youtube_channels():
    if os.path.isfile(youtube_channels_path):
        with open(youtube_channels_path, "r") as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                if len(line) > 0:
                    youtube_channels.append(line[0])
    else:
        print(youtube_channels_path, "is not exist.")
        sys.exit()

if __name__ == "__main__":
    main()

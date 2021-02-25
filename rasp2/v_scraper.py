from apiclient.discovery import build
from bs4 import BeautifulSoup
import datetime
import requests
import json


def youtube_channel(channel_id, api_key):
    api = build("youtube", "v3", developerKey = api_key)
    response = api.search().list(part = "id", channelId = channel_id, type = "video", eventType = "upcoming", maxResults = 50).execute()

    video_id_set = set()
    for item in response.get("items", []):
        video_id_set.add(item["id"]["videoId"])

    return video_id_set


def youtube_video(video_ids, api_key):
    api = build("youtube", "v3", developerKey = api_key)
    response = api.videos().list(part = "snippet, liveStreamingDetails", id = video_ids).execute()

    if response.get("items") is None:
        raise Exception("ERROR: v_scraper.youtube_video")

    videos = []
    for item in response.get("items"):
        video_id = item.get("id")
        if video_id is None:
            continue
        status = 6
        title = None
        start = None
        end = None
        if "snippet" in item:
            title = item["snippet"].get("title")
            liveBroadcastContent = item["snippet"].get("liveBroadcastContent")
        if "liveStreamingDetails" in item:
            scheduledStartTime = item["liveStreamingDetails"].get("scheduledStartTime")
            actualStartTime = item["liveStreamingDetails"].get("actualStartTime")
            actualEndTime = item["liveStreamingDetails"].get("actualEndTime")

            if scheduledStartTime is not None:
                status = 1
                start = datetime.datetime.fromisoformat(scheduledStartTime.replace("Z", "+00:00"))
            if actualStartTime is not None:
                status = 2
                start = datetime.datetime.fromisoformat(actualStartTime.replace("Z", "+00:00"))
            if actualEndTime is not None:
                status = 3
                end = datetime.datetime.fromisoformat(actualEndTime.replace("Z", "+00:00"))
        else:
            status = 4
        
        videos.append((video_id, status, title, start, end))

    return videos


def youtube_video_ytInitialData(video_id):
    web_page = requests.get("https://www.youtube.com/watch?v=" + video_id)
    soup = BeautifulSoup(web_page.text, "html.parser")

    # スクリプトタグ
    for script_tag in soup.find_all("script"):
        script_content = script_tag.string
        if script_content:
            if script_content.startswith("var ytInitialData"):
                try:
                    json_start = script_content.find("{")
                    json_end = script_content.rfind("}")
                    json_text = script_content[json_start : json_end + 1]
                    json_data = json.loads(json_text)
                    return json_data

                except Exception as e:
                    return None

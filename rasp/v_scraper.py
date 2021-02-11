from selenium.common.exceptions import NoSuchElementException
import requests
import re
import json
import urllib
import datetime
from bs4 import BeautifulSoup


re_freechat = re.compile("([ふフ][りリ]ー|free).*?([ちチ][ゃャ][っッ][とト]|chat)", re.IGNORECASE)


def youtube_channel(driver, channel_id):

    video_ids = set()

    # チャンネルページにアクセス
    url = "https://www.youtube.com/channel/" + channel_id
    driver.get(url)

    item_sections = driver.find_elements_by_tag_name("ytd-item-section-renderer")
    for item_section in item_sections:
        # 動画横一列分（セクション）

        try:
            # セクションのタイトル
            section_title = item_section.find_element_by_css_selector("div#title-container div#title-text")
            section_title_link = section_title.find_element_by_tag_name("a")
            section_title_link_url = section_title_link.get_attribute("href")

            if "live_view=501" in section_title_link_url or "live_view=502" in section_title_link_url:
                # ライブ配信中 or 今後のライブストリーム

                grid_videos = item_section.find_elements_by_tag_name("ytd-grid-video-renderer")

                if grid_videos:
                    # 動画が横に並んでいる

                    for grid_video in grid_videos:

                        video_link = grid_video.find_element_by_css_selector("a#video-title")
                        video_link_url = video_link.get_attribute("href")

                        if re_freechat.search(video_link.get_attribute("title")) is None:
                            video_ids.add(video_link_url.split("watch?v=")[-1])
                else:
                    # 横幅いっぱいに一つの動画

                    video = item_section.find_element_by_tag_name("ytd-video-renderer")
                    video_link = video.find_element_by_css_selector("a#video-title")
                    video_link_url = video_link.get_attribute("href")

                    if re_freechat.search(video_link.get_attribute("title")) is None:
                        video_ids.add(video_link_url.split("watch?v=")[-1])

        except NoSuchElementException:
            pass

    return video_ids


def youtube_embedded_live(channel_id):

    video_id = None

    # ライブ配信埋め込みURLにアクセス
    url = "https://www.youtube.com/embed/live_stream?channel=" + channel_id
    web_page = requests.get(url)
    soup = BeautifulSoup(web_page.text, "html.parser")

    title = soup.find("title") # " - YouTube" を含む
    link = soup.find("a")
    if link is not None and re_freechat.search(title.get_text()) is None:
        url_parse = urllib.parse.urlparse(link.get("href"))
        query = urllib.parse.parse_qs(url_parse.query)
        video_id = query["v"][0]

    return video_id


def youtube_video(video_id):

    url = "https://www.youtube.com/watch?v=" + video_id

    status_unplayable = False
    status_livestreamonline = False
    status_ok = False
    islivebroadcast = False

    status = 0
    title_text = None
    start_datetime = None
    end_datetime = None
    youtube_channel_ids = set()
    exists_chat = False

    web_page = requests.get(url)
    soup = BeautifulSoup(web_page.text, "html.parser")

    # スクリプトタグ
    for script_tag in soup.find_all("script"):
        script_content = script_tag.string
        if script_content:
            if "\"status\":\"UNPLAYABLE\"," in script_content:
                status_unplayable = True
            if "\"status\":\"LIVE_STREAM_OFFLINE\"," in script_content:
                status_livestreamonline = True
            if "\"status\":\"OK\"," in script_content:
                status_ok = True

            # ytInitialData
            if script_content.startswith("var ytInitialData"):
                try:
                    json_start = script_content.find("{")
                    json_end = script_content.rfind("}")
                    json_text = script_content[json_start : json_end + 1]
                    json_data = json.loads(json_text)

                    # 動画説明から YouTube チャンネルの URL を抽出
                    try:
                        descriptions = json_data["contents"]["twoColumnWatchNextResults"]["results"]["results"]["contents"][1]["videoSecondaryInfoRenderer"]["description"]["runs"]

                        for description in descriptions:
                            try:
                                link = description["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]
                                if link["webPageType"] == "WEB_PAGE_TYPE_CHANNEL":
                                    youtube_channel_ids.add(link["url"].split("/")[2])
                                elif link["webPageType"] == "WEB_PAGE_TYPE_UNKNOWN":
                                    url_parse = urllib.parse.urlparse(link["url"])
                                    if url_parse.netloc == "www.youtube.com" and url_parse.path.startswith("/channel/"):
                                        youtube_channel_ids.add(url_parse.path.split("/")[2])
                            except Exception as e:
                                pass

                    except Exception as e:
                        pass

                    # チャットが存在するか
                    try:
                        chat = json_data["contents"]["twoColumnWatchNextResults"]["conversationBar"]
                        exists_chat = True
                    except Exception as e:
                        exists_chat = False
                
                except Exception as e:
                    pass

    # タイトル
    title_meta = soup.find("meta", {"name" : "title"})
    if title_meta is not None:
        title_text = title_meta.get("content")

    # 開始日時
    start_meta = soup.find("meta", {"itemprop" : "startDate"})
    if start_meta is not None:
        start_datetime = datetime.datetime.fromisoformat(start_meta.get("content"))

    # 終了日時
    end_meta = soup.find("meta", {"itemprop" : "endDate"})
    if end_meta is not None:
        end_datetime = datetime.datetime.fromisoformat(end_meta.get("content"))

    # 配信ですか？
    islivebroadcast_meta = soup.find("meta", {"itemprop" : "isLiveBroadcast"})
    if islivebroadcast_meta is not None:
        #islivebroadcast_meta.get("content")
        islivebroadcast = True

    if status_unplayable:
        status = 5
    elif islivebroadcast:
        if status_livestreamonline:
            status = 1
        elif end_datetime is not None:
            status = 3
        else:
            status = 2
    elif status_ok:
        status = 4
    else:
        status = 6

    return status, title_text, start_datetime, end_datetime, youtube_channel_ids, exists_chat

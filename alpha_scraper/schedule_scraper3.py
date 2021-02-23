from apiclient.discovery import build
import feedparser
import pprint
import os
import sys


api_key_path = "youtube_data_api_key.txt"
api_key = ""
if os.path.isfile(api_key_path):
    with open(api_key_path, "r") as key_file:
        api_key = key_file.readline().splitlines()[0]
else:
    print(api_key_path, "is not exist.")
    sys.exit()


def youtube_channel(channel_id, api_key):
    api = build("youtube", "v3", developerKey = api_key)
    # response = api.activities().list(part = "snippet, contentDetails", channelId = channel_id).execute()
    # response = api.channelSections().list(part = "snippet, contentDetails", channelId = channel_id).execute()
    response = api.search().list(part = "id, snippet", channelId = channel_id, type = "video", eventType = "upcoming", maxResults = 50).execute()
    print(response)

    for item in response.get("items", []):
        try:
            del item["snippet"]["thumbnails"]
        except Exception as e:
            pass
        pprint.pprint(item)


def youtube_channel_feed(channel_id):
    feed = feedparser.parse("https://www.youtube.com/feeds/videos.xml?channel_id=" + channel_id)
    # print(feed)
    # pprint.pprint(feed)

    for entry in feed['entries']:
        # pprint.pprint(entry)
        # with open("tmp.txt", mode = "w", encoding = "utf_8") as f:
        #     f.write(str(entry))
        # break

        print(entry["link"])
        print(entry["title"])


def youtube_video(video_id, api_key):
    api = build("youtube", "v3", developerKey = api_key)
    response = api.videos().list(part = "snippet, liveStreamingDetails", id = video_id).execute()
    # print(response)

    # print(response.get("items"))
    print(len(response.get("items", [])))
    # for item in response.get("items", []):
    #     # print(item)

    #     # try:
    #     #     del item["kind"], item["etag"], item["snippet"]["thumbnails"], item["snippet"]["localized"], item["snippet"]["tags"]
    #     # except Exception as e:
    #     #     pass
    #     # pprint.pprint(item)

    #     print("id:", item.get("id"))
    #     if "snippet" in item:
    #         print("title:", item["snippet"].get("title"))
    #         if item["snippet"].get("description") is not None:
    #             print("description:", item["snippet"].get("description").replace("\n", ""))
    #         print("liveBroadcastContent: ", item["snippet"].get("liveBroadcastContent"))
    #     if "liveStreamingDetails" in item:
    #         print("scheduledStartTime:", item["liveStreamingDetails"].get("scheduledStartTime"))
    #         print("actualStartTime   :", item["liveStreamingDetails"].get("actualStartTime"))
    #         print("actualEndTime     :", item["liveStreamingDetails"].get("actualEndTime"))
    #     print()


if __name__ == "__main__":
    # 消去された配信
    # youtube_video("g4tCXx7tBWs", api_key)
    # 配信済み
    # youtube_video("G7IBLfDovwU", api_key)
    # 配信予定
    # youtube_video("khJugsohbuY", api_key)
    # メンバー限定
    # youtube_video("FLIIJlfguiY", api_key)
    # 配信ではない動画
    # youtube_video("WQYN2P3E06s", api_key)


    # youtube_video("ND-80ysmmVI,g4tCXx7tBWs", api_key)
    # youtube_video("1NoUu9_OIeQ,4Ag7sZrckO8,WzyWZqBFFaE,aEBxNU5j_Fs,hoFmVBBL5EQ,A07K2AqEtUc,5lGnmZsTT60,oLUCzLriVIg,-R3XgTU_2K4,tBrE2ztTKfM,2QSL9VmASLE,q9GolP7vQmk,sudrQYWd3Pc,4LVLICmRKRU,1S9GkxVSQ_s,GoW19wG5I0c,2vpNS_vkyag,MDHC_MProMs,71fCqz61F30,N3-XMkBkRE8,eeUTTn4H4n4,H3bk-lc3F8c,JEZ4OPPdlOM,CeAi9o6lxYM,EQLruCglPY8,GQdk0M2NoDs,EQuEKcVjYoI,OJ_Rk4OQC7k,kaeQ5lxNd_8,gxWkPUAh9VY,0aJOuuTucJk,4pWMwmkE3aI,M4R3EeCOYBQ,HjWlPONr1gM,Ear_hDih7kw,rAPmSv1qEOo,Tw4VimE89R0,glHcha0vVJk,50WbfsU_yTU,dtfl-6C3u-k,7RBvyU152oE,sCKSzgp_mfQ,dAiMpAgmdSo,8rC71jDL3Os,wUaWqNPNs7o,H31S-PGvmHo,u9yhjntbIcM,nhdrMAMt170,zHmc5xgjtBA,XOBeeAZ26TU,X3Dbe8j-lM8,R5tx6x7IjiU,i1EmRyVKu9U,jnj1TjPbVeI,R91jm4c2k3c,tMuZOzGd9mc,23eHJOloPy8,_x0bT3dfgEM,AxIrS_D_Bxk,ZGg7G2AWABg,VMVNfl5rqdk,6B85VN1CBs0,cO9h2iqCwbk,3l_U-x1L2iE,h3OvZfvrpyM,i6R_4noBL4I,WhHXyxUbw_k,OeoUyGeOkLY,qPLMDylxZM8,lKJ-jSw5dMM,-EzLZRI9Iqw,QgTQReXkotc,Mgba5wCRYZM,UbaX3moBESk,i_2dA0Yinoc,tOLFWtSOgq4,NGWGHnIPQn8,5iH0vffPDVY,IfrW7N8banU,WeEoTryaxPk,anAsR1u8CBU,XRmotX9y7Xs,IPIGKLsF7S4,28DXW-uDsmM,yGUlGkToowc,DMmJZ1q2ZN8,btKPhsiP2cc,drBpeu18kpY,bFlP1-ndW6s,rYczPZeTxXI,BJ9-ATTUKLQ,DrnpveGC1m0,O2Vf1Epz_XQ,37sypfwOnqA,DJlg7b9jbH8,JPORHDRHT6M,l2GKVoJ5PMw", api_key)

    # youtube_channel("UCg63a3lk6PNeWhVvMRM_mrQ")
    # youtube_channel("UCfipDDn7wY-C-SoUChgxCQQ")
    # youtube_channel("UCg63a3lk6PNeWhVvMRM_mrQ", api_key)
    # youtube_channel("UC2OacIzd2UxGHRGhdHl1Rhw", api_key)

import tkinter as tk
import tkinter.ttk as ttk
import youtube_dl
import urllib
import json
import os


class Window:


    def __init__(self):

        api_key_path = "api.key"
        if os.path.isfile(api_key_path):
            with open(api_key_path, "r") as key_file:
                self.server_url = key_file.readline().splitlines()[0]
        else:
            raise Exception(api_key_path + " does not exist.")

        root = tk.Tk()
        root.title("Editor Manager")

        # 通信
        request = urllib.request.Request(self.server_url + "/api/analyzed-video-list", data = "".encode(), method = "POST")
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read())
        video_list = data["video_list"]

        # 画面組立
        for i, video in enumerate(video_list):
            number = ttk.Label(root, text = video["id"])
            number.grid(row = i, column = 0, sticky = tk.E)
            title = ttk.Label(root, text = video["title"])
            title.grid(row = i, column = 1, sticky = tk.W)
            button = ttk.Button(root, text = "↓", command = self.push_button(video["id"]))
            button.grid(row = i, column = 2)

        root.mainloop()

    def push_button(self, video_id):
        def f():
            self.process_video(video_id)
        return f

    def process_video(self, video_id):

        # 通信
        request = urllib.request.Request(self.server_url + "/api/video-analysis", data = json.dumps({"video_id": video_id}).encode(), method = "POST")
        with urllib.request.urlopen(request) as response:
            data = json.loads(response.read())
        title = data["title"]
        youtube_video_id = data["youtube_video_id"]
        analysis_data = json.loads(data["analysis"])
        clip_times = analysis_data["clip_times"]

        # ディレクトリ
        dirpath = os.path.abspath(os.path.join(os.path.dirname(__file__), "V" + str(video_id) + "_" + youtube_video_id)) #  + "_" + title[:10]))
        if os.path.exists(dirpath):
            if not os.path.isdir(dirpath):
                raise Exception(dirpath + "is not directory.")
        else:
            os.mkdir(dirpath)

        # 動画
        video_filename = download("https://www.youtube.com/watch?v=" + youtube_video_id, dirpath)

        # スクリプト
        with open(os.path.join(dirpath, "resolver.lua"), "w") as pyfile:
            pyfile.write(resolve_script_lua("V" + str(video_id) + "_" + youtube_video_id, os.path.join(dirpath, video_filename), clip_times))

        print("完了", "V" + str(video_id) + "_" + youtube_video_id, title)


def download(url, dirpath):
    ydl_opts = {"format" : "best", "outtmpl" : dirpath + "/%(id)s.%(ext)s"}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            filename = info_dict["id"] + "." + info_dict["ext"]

            if not os.path.isfile(os.path.join(dirpath, filename)):
                ydl.download([url])

            return filename
    except Exception:
        raise Exception("Video cannot be downloaded.")


def resolve_script_lua(title, video_abspath, clip_times):
    script_1 = """
title = \"""" + title + """\"
video_path = \"""" + video_abspath.replace("\\", "\\\\") + """\"

print("CREATE project")
resolve = Resolve()
projectManager = resolve:GetProjectManager()
project = projectManager:CreateProject(title)
if not project then
	print(" ERROR")
	os.exit()
end

print("LOAD video")
mediaPool = project:GetMediaPool()
rootFolder = mediaPool:GetRootFolder()
videos = resolve:GetMediaStorage():AddItemsToMediaPool(video_path)
for index in pairs(videos) do
    video = videos[index]
end

video_resolution = video:GetClipProperty()["Resolution"]
video_fps = video:GetClipProperty()["FPS"]

project:SetSetting("timelineFrameRate", video_fps)
i = 1
for s in string.gmatch(video_resolution, "([^x]+)") do
    if i == 1 then
        project:SetSetting("timelineResolutionWidth", s)
    else
        project:SetSetting("timelineResolutionHeight", s)
    end
    i = i + 1
end

print("TIMELINE")
timeline = mediaPool:CreateEmptyTimeline("Timeline 1")
if not timeline then
	print(" ERROR")
	os.exit()
end

print("ADD video")
"""

    script_2 = ""
    for clip_time in clip_times:
        clip_start = clip_time[0].strip("\"").strip("'")
        clip_end = clip_time[1].strip("\"").strip("'")
        script_2 += "s = math.floor(tonumber(video_fps) * " + clip_start + ")\n"
        script_2 += "e = math.floor(tonumber(video_fps) * " + clip_end + ")\n"
        script_2 += "print(s .. \" \" .. e)\n"
        script_2 += "mediaPool:AppendToTimeline({{mediaPoolItem = video, startFrame = s, endFrame = e}})\n"

    return script_1 + script_2


if __name__ == "__main__":
    Window()

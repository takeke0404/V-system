import csv
import os
import sys

dir_path = ""
csv_filename = "test" + ".csv"

print("LOAD CSV")
csv_path = os.path.join(dir_path, csv_filename)
if os.path.isfile(csv_path):
    url = None
    clip_times = []
    with open(csv_path, "r") as csv_file:
        reader = csv.reader(csv_file)
        for line in reader:
            if url is None:
                if len(line) > 0:
                    url = line[0]
            else:
                if len(line) > 1:
                    clip_times.append((float(line[0]), float(line[1])))
else:
    print("ERROR:", csv_path, "does not exist.")
    sys.exit()

video_id = url.split("=")[-1].strip()

video_path = os.path.join(dir_path, video_id + ".mp4")
if not os.path.isfile(video_path):
    print("ERROR:", csv_path, "does not exist.")
    sys.exit()

export_path = dir_path

print("CREATE PROJECT")
projectManager = resolve.GetProjectManager()
project = projectManager.CreateProject("TEST")

print("MEDIA")
mediapool = project.GetMediaPool()
rootFolder = mediapool.GetRootFolder()

print("LOAD VIDEO")
video1 = resolve.GetMediaStorage().AddItemsToMediaPool(video_path)

video2 = rootFolder.GetClipList()[0]
#print(video2)
#print(video2.GetClipProperty())
#print(video2.GetClipProperty()["Video Codec"])
#print(video2.GetClipProperty()["Resolution"])
#print(video2.GetClipProperty()["FPS"])
video_size_str = video2.GetClipProperty()["Resolution"].split("x")
video_fps = float(video2.GetClipProperty()["FPS"])

print("size", video_size_str)
print("fps", video_fps)

project.SetSetting("timelineFrameRate", str(video_fps))
project.SetSetting("timelineResolutionWidth", video_size_str[0])
project.SetSetting("timelineResolutionHeight", video_size_str[1])

print("TIMELINE")
timeline = mediapool.CreateEmptyTimeline("Timeline 1")

print("ADD VIDEO")
for clip in clip_times:
    print("frame", int(clip[0] * video_fps), int(clip[1] * video_fps))
    clip_part = {
        "mediaPoolItem": video2,
        "startFrame": int(clip[0] * video_fps),
        "endFrame": int(clip[1] * video_fps),
    }
    mediapool.AppendToTimeline([clip_part])

print("SAVE")
#projectManager.SaveProject()
a = projectManager.ExportProject("EXPORT_TEST", export_path)
print(a)

print("END")

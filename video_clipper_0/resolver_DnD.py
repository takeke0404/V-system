
video_path = ""
export_path = ""
clip_time = [[203.74,213.76],
[244.94,255.6],
[455.92,488.1],
[512.12,546.82],
[836.56,843.84],
[1278.24,1297.94],
[1317.14,1355.34],
[1454.98,1480.0],
[1548.04,1555.36],
[1565.64,1570.74],
[1609.16,1621.7],
[4051.44,4059.7],
[5207.54,5237.44],
[6469.2,6482.94],
[6727.26,6740.82],
[7965.84,7988.0],
[10038.52,10054.64]]



print("START")

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

for clip_t in clip_time:
    print("frame", int(clip_t[0] * video_fps), int(clip_t[1] * video_fps))
    clip_part = {
        "mediaPoolItem": video2,
        "startFrame": int(clip_t[0] * video_fps),
        "endFrame": int(clip_t[1] * video_fps),
    }
    mediapool.AppendToTimeline([clip_part])

print("SAVE")

#projectManager.SaveProject()
a = projectManager.ExportProject("EXPORT_TEST", export_path)
print(a)

print("END")

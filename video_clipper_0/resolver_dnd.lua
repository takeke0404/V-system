title = "4Ag7sZrckO8_【雑談】"
video_path = ""

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
mediaPool:AppendToTimeline({{mediaPoolItem = video, startFrame = 200, endFrame = 400}})
mediaPool:AppendToTimeline({{mediaPoolItem = video, startFrame = 800, endFrame = 1600}})

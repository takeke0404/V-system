import csv
import cv2
import youtube_dl
import os
import sys

import get_video

"""
整数でないフレームレート
音声レート・チャンネル
フェードインアウト
"""

def main():

    # csv ファイルの検索
    csv_files = search_csv()
    if not csv_files:
        print("There is no csv file.")
        sys.exit()

    for csv_file in csv_files:
        # csv ファイルの読み込み
        url, clip_times = load_csv(csv_file)
        print(url)
        print(clip_times)

        if url:
            id = url.split("=")[-1].strip()
            print(id)

            video_filename = id + ".mp4" # とりあえず MP4 と仮定する。
            if not os.path.isfile(video_filename):
                video_filename = get_video.download(url)
            video_abspath = os.path.abspath(os.path.join(os.path.dirname(__file__), video_filename))

            # 動画読み込み
            video = cv2.VideoCapture(video_filename)
            width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = video.get(cv2.CAP_PROP_FPS)
            length = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

            print(width, height, fps, length)


            exo_filename = id + ".exo"
            with open(exo_filename, "w", encoding = "shift_jis") as exo_file:

                # 切り抜き秒数からフレーム数へ
                total_frame = 0
                clip_frames = []
                for clip_time in clip_times:
                    start_frame = min(max(1, int(clip_time[0] * fps)), length)
                    end_frame = min(max(1, int(clip_time[1] * fps)), length)

                    total_frame += 1
                    total_frame2 = total_frame + end_frame - start_frame
                    clip_frames.append((total_frame, total_frame2, start_frame))
                    total_frame = total_frame2

                #exo_file.write("")
                exo_file.write("[exedit]\n")
                exo_file.write("width=" + str(width) + "\n")
                exo_file.write("height=" + str(height) + "\n")
                exo_file.write("rate=" + str(int(fps)) + "\n")
                exo_file.write("scale=1\n")
                exo_file.write("length=" + str(total_frame) + "\n")
                exo_file.write("audio_rate=" + "44100" + "\n")
                exo_file.write("audio_ch=" + "2" + "\n")

                total_i = 0
                for i, clip_frame in enumerate(clip_frames):
                    exo_file.write("[" + str(total_i) + "]\n")
                    exo_file.write("start=" + str(clip_frame[0]) + "\n")
                    exo_file.write("end=" + str(clip_frame[1]) + "\n")
                    exo_file.write("layer=1\n")
                    exo_file.write("group=" + str(i + 1) + "\n")
                    exo_file.write("overlay=1\n")
                    exo_file.write("camera=0\n")
                    exo_file.write("[" + str(total_i) + ".0]\n")
                    exo_file.write("_name=動画ファイル\n")
                    exo_file.write("再生位置=" + str(clip_frame[2]) + "\n")
                    exo_file.write("再生速度=100.0\n")
                    exo_file.write("ループ再生=0\n")
                    exo_file.write("アルファチャンネルを読み込む=0\n")
                    exo_file.write("file=" + video_abspath + "\n")
                    exo_file.write("[" + str(total_i) + ".1]\n")
                    exo_file.write("_name=標準描画\n")
                    exo_file.write("X=0.0\n")
                    exo_file.write("Y=0.0\n")
                    exo_file.write("Z=0.0\n")
                    exo_file.write("拡大率=100.00\n")
                    exo_file.write("透明度=0.0\n")
                    exo_file.write("回転=0.00\n")
                    exo_file.write("blend=0\n")
                    total_i += 1

                for i, clip_frame in enumerate(clip_frames):
                    exo_file.write("[" + str(total_i) + "]\n")
                    exo_file.write("start=" + str(clip_frame[0]) + "\n")
                    exo_file.write("end=" + str(clip_frame[1]) + "\n")
                    exo_file.write("layer=2\n")
                    exo_file.write("group=" + str(i + 1) + "\n")
                    exo_file.write("overlay=1\n")
                    exo_file.write("audio=1\n")
                    exo_file.write("[" + str(total_i) + ".0]\n")
                    exo_file.write("_name=音声ファイル\n")
                    exo_file.write("再生位置=0.00\n")
                    exo_file.write("再生速度=100.0\n")
                    exo_file.write("ループ再生=0\n")
                    exo_file.write("動画ファイルと連携=1\n")
                    exo_file.write("file=" + video_abspath + "\n")
                    exo_file.write("[" + str(total_i) + ".1]\n")
                    exo_file.write("_name=標準再生\n")
                    exo_file.write("音量=100.0\n")
                    exo_file.write("左右=0.0\n")
                    total_i += 1

                exo_file.write("")

                print(exo_filename)

def search_csv():
    csv_files = []
    for item in os.listdir():
        if os.path.isfile(item) and item.endswith(".csv"):
            csv_files.append(item)
    return csv_files

def load_csv(path):
    if os.path.isfile(path):
        url = None
        clip_times = []
        with open(path, "r") as csv_file:
            reader = csv.reader(csv_file)
            for line in reader:
                if url:
                    if len(line) > 1:
                        clip_times.append((float(line[0]), float(line[1])))
                else:
                    if len(line) > 0:
                        url = line[0]
        return url, clip_times
    else:
        return None, None

if __name__ == "__main__":
    main()

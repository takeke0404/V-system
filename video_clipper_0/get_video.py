import youtube_dl
import os

def download(url):
    ydl_opts = {"format" : "best", "outtmpl" : '\\%(id)s.%(ext)s'}
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)

            filename = info_dict["id"] + "." + info_dict["ext"]
            print(filename, info_dict["title"])

            if not os.path.isfile(filename):
                ydl.download([url])

            return filename
    except Exception:
        return False

if __name__ == "__main__":
    download("https://www.youtube.com/watch?v=zLE2pqnLgXw")

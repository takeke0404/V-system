import youtube_dl

def download(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': '\\%(id)s.%(ext)s',
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            print(info_dict["id"] + "." + info_dict["ext"])
            print(info_dict["title"])
            print(info_dict["format"])
            ydl.download([url])
    except Exception:
        return False

if __name__ == "__main__":
    download("https://www.youtube.com/watch?v=zLE2pqnLgXw")

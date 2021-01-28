import requests
import os


class Manager:


    def __init__(self):
        self.mler_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mler.key")
        self.mler_url = None


    def post(self, youtube_video_id):

        if self.mler_url is None:
            if os.path.isfile(self.mler_key_path):
                with open(self.mler_key_path, "r") as key_file:
                    self.mler_url = key_file.readline().splitlines()[0]
            else:
                raise Exception("mler:" + self.mler_key_path + " does not exist.")


        response = requests.post(self.mler_url + "/post_url", data = {"youtube_url" : "https://www.youtube.com/watch?v=" + youtube_video_id})

        return response


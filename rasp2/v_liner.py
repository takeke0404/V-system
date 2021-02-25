import requests
import os


class Manager:

    def __init__(self):
        line_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "line.key")
        self.line_access_token = None
        self.line_notify_url = "https://notify-api.line.me/api/notify"

        if os.path.isfile(line_key_path):
            with open(line_key_path, "r") as key_file:
                self.line_access_token = key_file.readline().splitlines()[0]
        else:
            raise Exception("LINE:" + line_key_path + " does not exist.")


    def send(self, message):
        requests.post(self.line_notify_url, headers = {"Authorization": "Bearer " + self.line_access_token}, params = {"message": message, "notificationDisabled": "true"})

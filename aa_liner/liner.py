import requests
import os


def main():

        line_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "line.key")
        line_access_token = None
        line_notify_url = "https://notify-api.line.me/api/notify"

        if os.path.isfile(line_key_path):
            with open(line_key_path, "r") as key_file:
                line_access_token = key_file.readline().splitlines()[0]
        else:
            raise Exception(line_key_path + " is not exist.")

        headers = {"Authorization": "Bearer " + line_access_token}
        payload = {"message": "行きなさいシンジ君。誰かのためじゃない、あなた自身の願いのために。", "notificationDisabled": "true"}
        requests.post(line_notify_url, headers = headers, params = payload)


if __name__ == "__main__":
    main()

import requests
import sys
import csv
import json

if __name__ == "__main__":
    args = sys.argv
    json_list = []
    with open("./summarization_by_comment_count_and_bert/"+args[1]+".csv") as f:
        for row in csv.reader(f):
            json_list.append(row)
    response = requests.post("http://192.168.1.102:58539/api/video-analyzed",json.dumps(json_list))
    if(response.status_code == requests.codes.ok):
        print("送信成功")
    else:
        print("送信失敗")

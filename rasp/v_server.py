import flask
import json
import os

import v_mysql
import v_liner
import v_mler


server_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "server.key")

if os.path.isfile(server_key_path):
    with open(server_key_path, "r") as key_file:
        server_url = key_file.readline().splitlines()[0]
else:
    raise Exception("Server:" + server_key_path + " does not exist.")

database = v_mysql.Manager()
liner = v_liner.Manager()
mler = v_mler.Manager()

app = flask.Flask(__name__)


@app.route("/")
def index():
    return "V on Raspberry Pi"


@app.route("/api/video-analyzed", methods = ["POST"])
def video_analyzed():
    try:
        data = json.loads(flask.request.get_data())

        youtube_video_id = data[0][0].split("watch?v=")[-1]
        data_str = json.dumps({"clip_times" : data[1:]})

        mler.process_analysis_status(youtube_video_id, 4, data_str)

        return flask.Response(response = "received", status = 200)
    except Exception as e:
        return flask.Response(response = "error", status = 500)


if __name__ == "__main__":
    app.run("0.0.0.0", port = server_url.split(":")[-1])


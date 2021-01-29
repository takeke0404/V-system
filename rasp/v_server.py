import flask
import json
import os

import v_liner


server_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "server.key")

if os.path.isfile(server_key_path):
    with open(server_key_path, "r") as key_file:
        server_url = key_file.readline().splitlines()[0]

liner = v_liner.Manager()

app = flask.Flask(__name__)


@app.route("/")
def index():
    return "V on Raspberry Pi"


@app.route("/api/video-analyzed", methods = ["POST"])
def video_analyzed():

    data = flask.request.get_data()
    print(data)

    liner.send(str(data))

    return flask.Response(response = json.dumps(["received"]), status = 200)


if __name__ == "__main__":
    app.run("0.0.0.0", port = server_url.split(":")[-1])


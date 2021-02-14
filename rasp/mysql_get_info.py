import v_mysql


def main():
    database = v_mysql.Manager()

    database.connect()
    vtubers = database.execute("SELECT id, youtube_channel_id, name, editor_id FROM vtuber;")
    database.close()

    for vtuber in vtubers:
        print(vtuber)

    database.connect()
    videos = database.execute("SELECT * FROM video;")
    database.close()

    for video in videos:
        print(video)


if __name__ == "__main__":
    main()

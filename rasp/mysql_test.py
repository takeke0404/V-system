import mysql.connector
import os
import sys

mysql_key_path = "mysql.key"

def main():

    if os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), mysql_key_path))):
        with open(os.path.abspath(os.path.join(os.path.dirname(__file__), mysql_key_path)), "r") as key_file:
            mysql_host = key_file.readline().splitlines()[0]
            mysql_port = key_file.readline().splitlines()[0]
            mysql_user = key_file.readline().splitlines()[0]
            mysql_password = key_file.readline().splitlines()[0]
            mysql_database = key_file.readline().splitlines()[0]
    else:
        print(os.path.abspath(os.path.join(os.path.dirname(__file__), mysql_key_path)), "is not exist.")
        sys.exit()

    connection = mysql.connector.connect(
        host = mysql_host,
        port = mysql_port,
        user = mysql_user,
        password = mysql_password,
        database = mysql_database
    )

    cursor = connection.cursor()

    #cursor.execute("SELECT youtube_channel_id FROM vtuber")
    #print(cursor.fetchall())

    cursor.execute("SELECT * FROM vtuber")
    print(cursor.fetchall())

    #cursor.execute("INSERT INTO vtuber (name, youtube_channel_id) VALUES ('鷹宮リオン', 'UCV5ZZlLjk5MKGg3L0n0vbzw');")
    #print(cursor.fetchall())
    #cursor.close()
    #connection.commit()
    #cursor = connection.cursor()

    cursor.execute("SELECT * FROM video")
    a = cursor.fetchall()
    print(a)
    #print(a[0][5])

    cursor.execute("SELECT id, youtube_video_id FROM video WHERE status=1 OR status=2;")
    print(cursor.fetchall())

    cursor.close()
    connection.close()

if __name__ == "__main__":
    main()

import mysql.connector
import os


class Manager:


    def __init__(self):

        self.mysql_host = None
        self.mysql_port = None
        self.mysql_user = None
        self.mysql_password = None
        self.mysql_database = None
        self.connection = None
        self.cursor = None

        mysql_key_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "mysql.key")

        if os.path.isfile(mysql_key_path):
            with open(mysql_key_path, "r") as key_file:
                self.mysql_host = key_file.readline().splitlines()[0]
                self.mysql_port = key_file.readline().splitlines()[0]
                self.mysql_user = key_file.readline().splitlines()[0]
                self.mysql_password = key_file.readline().splitlines()[0]
                self.mysql_database = key_file.readline().splitlines()[0]
        else:
            raise Exception("MySQL: init " + mysql_key_path + " does not exist.")


    def connect(self):
        self.connection = mysql.connector.connect(
            host = self.mysql_host,
            port = self.mysql_port,
            user = self.mysql_user,
            password = self.mysql_password,
            database = self.mysql_database
        )
        self.cursor = self.connection.cursor()


    def execute(self, statement, data = None):
        if self.connection is None:
            self.connect()
        if not self.connection.is_connected():
            self.connect()

        if data is None:
            self.cursor.execute(statement)
        else:
            self.cursor.execute(statement, data)
        return self.cursor.fetchall()


    def executemany(self, statement, data):
        if self.connection is None:
            self.connect()
        if not self.connection.is_connected():
            self.connect()

        self.cursor.executemany(statement, data)
        return self.cursor.fetchall()


    def close(self):
        self.cursor.close()
        self.connection.commit()
        self.connection.close()


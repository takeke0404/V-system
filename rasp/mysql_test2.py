import v_mysql


def main():
    database = v_mysql.Manager()

    database.connect()
    print(database.execute("SELECT * FROM test;"))
    database.close()

    database.connect()
    database.execute("INSERT INTO test (name) VALUES ('a');")
    print(database.execute("SELECT LAST_INSERT_ID();"))
    database.close()

    database.connect()
    print(database.execute("SELECT * FROM test;"))
    database.close()


if __name__ == "__main__":
    main()


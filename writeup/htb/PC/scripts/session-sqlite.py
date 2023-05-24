import sqlite3
def read_session_sqlite(file_path):

    conn = sqlite3.connect(file_path)
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"Table: {table_name}\n-------------------------")

        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()

        for row in rows:print(row)

    cursor.close()
    conn.close()

if __name__ == '__main__':
    sqlite_file = "<path>/session.sqlite"
    read_session_sqlite(sqlite_file)
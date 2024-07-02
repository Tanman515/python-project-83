import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.extensions import AsIs


def insert_into_db(DATABASE_URL, table_name, insert_data):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        with conn.cursor() as cursor:
            columns = insert_data.keys()
            values = [insert_data[column] for column in columns]
            insert_statement = f'INSERT INTO {table_name} (%s) VALUES %s'
            cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    except Exception as error:
        print('[INFO] Can`t establish connection to database')
        print(error)
    finally:
        conn.close()
        print('[INFO] Connection closed')


def read_db(DATABASE_URL, table_name, order='ASC'):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            if order == 'ASC':
                cursor.execute(f"SELECT * FROM {table_name};")
            elif order == 'DESC':
                cursor.execute(f"SELECT * FROM {table_name} ORDER BY id DESC;")
            records = cursor.fetchall()
            records = [dict(record) for record in records]
        return records
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()


class DataBase:

    def __init__(self, DATABASE_URL):
        self.DATABASE_URL = DATABASE_URL

    def connect(self):
        pass

    def read(self, order='ASC'):
        pass

    def insert(self, id, current_url, created_at):
        pass

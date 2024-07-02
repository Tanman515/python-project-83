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


def join_dbs(DATABASE_URL, table1, table2):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute(f"""SELECT {table1}.id AS id, {table1}.url AS url, url_checks.created_at AS created_at
                             FROM {table1}
                             LEFT JOIN (SELECT url_id, MAX(created_at) AS created_at
                                        FROM {table2}
                                        GROUP BY url_id) AS url_checks
                             ON {table1}.id = url_checks.url_id
                             ORDER BY {table1}.id DESC;""")
            records = cursor.fetchall()
            records = [dict(record) for record in records]
            print(records)
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

    def read(self, table, order='ASC'):
        pass

    def join(self, table1, table2):
        pass

    def insert(self, values):
        pass

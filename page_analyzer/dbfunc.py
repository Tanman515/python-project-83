import psycopg2


def insert_into_db(DATABASE_URL, id, current_url, created_at):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        with conn.cursor() as cursor:
            cursor.execute("INSERT INTO urls (id, url, created_at) VALUES (%s, %s, %s);", (id, current_url, created_at)) # noqa
    except Exception as error:
        print('[INFO] Can`t establish connection to database')
        print(error)
    finally:
        conn.close()
        print('[INFO] Connection closed')


def read_db(DATABASE_URL, order='ASC'):
    try:
        conn = psycopg2.connect(DATABASE_URL)
        with conn.cursor() as cursor:
            if order == 'ASC':
                cursor.execute("SELECT * FROM urls;")
            elif order == 'DESC':
                cursor.execute("SELECT * FROM urls ORDER BY id DESC;")
            data = cursor.fetchall()
            _dict = [{'id': i, 'url': u, 'created_at': c} for i, u, c in data]
        return _dict
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        conn.close()

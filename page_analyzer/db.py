import psycopg2
from psycopg2.extras import NamedTupleCursor
from psycopg2.extensions import AsIs


class DataBase:

    """
    This class uses psycopg2 for formation and execution sql query.

    It can be used for insert, read or join data in special cases.

    If you want to use this class, you dont need to connect to db.
    This class will do it for you.
    """

    def __init__(self, DATABASE_URL):
        self.DATABASE_URL = DATABASE_URL

    def _connect(self):
        return psycopg2.connect(self.DATABASE_URL)

    def read_all_data(self, dbname):
        NamedTuples = None
        with self._connect() as connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(f'SELECT * FROM {dbname}')
                NamedTuples = cursor.fetchall()
                print(f'[INFO] Data from db "{dbname}" was selected by "read_all_data" function')
        connection.close()
        print(f'[INFO] Connection was closed "{dbname}"')

        if NamedTuples:
            return [NamedTuple._asdict() for NamedTuple in NamedTuples]
        else:
            return []

    def insert(self, dbname, data):
        with self._connect() as connection:
            with connection.cursor() as cursor:
                columns = data.keys()
                values = [data[column] for column in columns]
                insert_statement = f'INSERT INTO {dbname} (%s) VALUES %s'
                cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
                connection.commit()
                print("[INFO] Data was saved by 'insert' function")
        connection.close()
        print(f'[INFO] Connection was closed "{dbname}"')

    def get_record_by_url_id(self, dbname, url_id):
        NamedTuple = None
        with self._connect() as connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                query = f'SELECT * FROM {dbname} WHERE id = %s'
                cursor.execute(query, (url_id,))
                NamedTuple = cursor.fetchone()
                print(f'[INFO] Data from db "{dbname}" was selected by "get_record_by_url" function')
        connection.close()
        print(f'[INFO] Connection was closed "{dbname}"')

        if NamedTuple:
            return NamedTuple._asdict()
        else:
            return {}

    def get_checks_by_url_id(self, dbname, url_id):
        NamedTuples = None
        with self._connect() as connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                query = f'SELECT * FROM {dbname} WHERE url_id = %s ORDER BY id DESC'
                cursor.execute(query, (url_id,))
                NamedTuples = cursor.fetchall()
                print(f'[INFO] Data from db "{dbname}" was selected by "get_checks_by_url" function')
        connection.close()
        print(f'[INFO] Connection was closed "{dbname}"')

        if NamedTuples:
            return [NamedTuple._asdict() for NamedTuple in NamedTuples]
        else:
            return []

    def join_url_checks(self, dbname1, dbname2):
        NamedTuples = None
        with self._connect() as connection:
            with connection.cursor(cursor_factory=NamedTupleCursor) as cursor:
                cursor.execute(f"""SELECT {dbname1}.id AS id,
                                          {dbname1}.url AS url,
                                          url_checks.created_at AS created_at,
                                          url_checks.status_code
                             FROM {dbname1}
                             LEFT JOIN (SELECT url_id, created_at, status_code,
                                        ROW_NUMBER() OVER (
                                            PARTITION BY url_id
                                            ORDER BY created_at DESC) AS rn
                                        FROM {dbname2}) AS url_checks
                             ON {dbname1}.id = url_checks.url_id AND url_checks.rn = 1
                             ORDER BY {dbname1}.id DESC;""")
                NamedTuples = cursor.fetchall()
                print('[INFO] Join data was finished')
        connection.close()
        print(f'[INFO] Connection was closed "{dbname1}" "{dbname2}"')

        if NamedTuples:
            return [NamedTuple._asdict() for NamedTuple in NamedTuples]
        else:
            return []

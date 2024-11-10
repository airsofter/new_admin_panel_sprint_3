import psycopg
from config import DATABASE


class PostgresDB:
    def __init__(self):
        self.connection = psycopg.connect(
            host=DATABASE["host"],
            port=DATABASE["port"],
            dbname=DATABASE["dbname"],
            user=DATABASE["user"],
            password=DATABASE["password"],
        )

    def fetch_movies(self, last_processed_id=None):
        query = "SELECT * FROM movies WHERE id > %s ORDER BY id;"
        with self.connection.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute(query, (last_processed_id,))
            return cursor.fetchall()

    def close(self):
        self.connection.close()

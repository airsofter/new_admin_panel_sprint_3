import psycopg
from typing import Generator, List, Dict, Any, Optional
from psycopg.rows import dict_row
from contextlib import closing
from logging_config import logger
from config import BATCH_SIZE, DATABASE
from backoff import backoff


class PostgresClient:
    """Клиент для взаимодействия с PostgreSQL."""
    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def fetch_records(
        self, query: str, params: Optional[tuple] = None, batch_size: int = BATCH_SIZE
    ) -> Generator[Dict[str, Any], None, None]:
        with closing(psycopg.connect(**DATABASE)) as conn:
            try:
                with conn.cursor(row_factory=dict_row) as cursor:
                    cursor.execute(query, params)

                    while True:
                        records = cursor.fetchmany(batch_size)
                        if not records:
                            break
                        yield from records
            except Exception as e:
                logger.error(f"Ошибка при выполнении запроса: {e}")

    def get_updated_person_ids(
        self, last_modified: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Получает список обновленных персон."""
        query = """
            SELECT id, modified
            FROM content.person
            WHERE modified > %s
            ORDER BY modified;
        """

        return self.fetch_records(query, (last_modified,))

    def get_film_ids_by_person_ids(
        self, person_ids: List[str]
    ) -> Generator[Dict[str, Any], None, None]:
        """Получает ID фильмов по списку ID персон"""
        query = """
            SELECT fw.id, fw.modified
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.person_id = ANY(%s)
            ORDER BY fw.modified;
        """
        return self.fetch_records(query, (person_ids,))

    def get_updated_genre_ids(
        self, last_modified: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Получает список обновленных жанров."""
        query = """
            SELECT id as id, modified
            FROM content.genre
            WHERE modified > %s
            ORDER BY modified;
        """
        return self.fetch_records(query, (last_modified,))

    def get_film_ids_by_genre_ids(
        self, genre_ids: List[str]
    ) -> Generator[Dict[str, Any], None, None]:
        """"Получает ID фильмов по списку ID жанров"""
        query = """
            SELECT fw.id, fw.modified
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            WHERE gfw.genre_id = ANY(%s)
            ORDER BY fw.modified;
        """
        return self.fetch_records(query, (genre_ids,))

    def get_updated_film_ids(
        self, last_modified: str
    ) -> Generator[Dict[str, Any], None, None]:
        """Получает список обновленных фильмов."""
        query = """
            SELECT id, modified
            FROM content.film_work
            WHERE modified > %s
            ORDER BY modified;
        """
        return self.fetch_records(query, (last_modified,))

    def get_film_details(
        self, film_ids: List[str]
    ) -> Generator[Dict[str, Any], None, None]:
        """Получает подробную информацию о фильмах."""
        query = """
            SELECT
                fw.id as fw_id,
                fw.title as title,
                fw.description as description,
                fw.rating as rating,
                fw.type as genres,
                fw.created,
                fw.modified,
                pfw.role,
                p.id AS person_id,
                p.full_name AS person_name,
                g.name AS genre_name
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            LEFT JOIN content.person p ON p.id = pfw.person_id
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            LEFT JOIN content.genre g ON g.id = gfw.genre_id
            WHERE fw.id = ANY(%s);
        """
        return self.fetch_records(query, (film_ids,))

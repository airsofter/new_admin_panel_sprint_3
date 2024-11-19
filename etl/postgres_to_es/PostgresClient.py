import psycopg
import logging
from typing import List, Dict, Any, Tuple
from config import DATABASE_LOCAL
# from StateManager import StateManager
# from ElasticSearchClient import Elasticsearch
from psycopg.rows import dict_row
from contextlib import closing
from backoff import backoff
# TODO: убрать лишнее


class PostgresClient:
    # def __init__(self):
    #     self.connection = psycopg.connect(**DATABASE)

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def fetch_records(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Выполняет запрос к базе данных и возвращает список словарей с результатами."""
        with closing(psycopg.connect(**DATABASE_LOCAL)) as conn:
            with conn.cursor(row_factory=dict_row) as cursor:
                cursor.execute(query, params)
                records = cursor.fetchall()
        return records

    def get_updated_person_ids(self, last_modified: str) -> List[Dict[str, Any]]:
        query = """
            SELECT id as id, modified
            FROM content.person
            WHERE modified > %s
            ORDER BY modified
            LIMIT 100;
        """

        return self.fetch_records(query, (last_modified,))

    def get_film_ids_by_person_ids(self, person_ids: str) -> List[Dict[str, Any]]:
        query = """
            SELECT fw.id, fw.modified
            FROM content.film_work fw
            LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
            WHERE pfw.person_id = ANY(%s)
            ORDER BY fw.modified
            LIMIT 100;
        """
        return self.fetch_records(query, (person_ids,))

    def get_updated_genre_ids(self, last_modified: str) -> List[Dict[str, Any]]:
        query = """
            SELECT id as id, modified
            FROM content.genre
            WHERE modified > %s
            ORDER BY modified
            LIMIT 100;
        """
        return self.fetch_records(query, (last_modified,))

    def get_film_ids_by_genre_ids(self, genre_ids: List[str]) -> List[Dict[str, Any]]:
        query = """
            SELECT fw.id , fw.modified
            FROM content.film_work fw
            LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
            WHERE gfw.genre_id = ANY(%s)
            ORDER BY fw.modified
            LIMIT 100;
        """
        return self.fetch_records(query, (genre_ids,))

    def get_updated_film_ids(self, last_modified: str) -> List[Dict[str, Any]]:
        query = """
            SELECT id, modified
            FROM content.film_work
            WHERE modified > %s
            ORDER BY modified
            LIMIT 100;
        """
        return self.fetch_records(query, (last_modified,))

    def get_film_details(self, film_ids: List[str]) -> List[Dict[str, Any]]:
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



# class PostgresClient:
#     # def __init__(self):
#     #     self.connection = psycopg.connect(**DATABASE)

#     @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
#     def fetch_records(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
#         """Выполняет запрос к базе данных и возвращает список словарей с результатами."""
#         with closing(psycopg.connect(**DATABASE_LOCAL)) as conn:
#             with conn.cursor(row_factory=dict_row) as cursor:
#                 cursor.execute(query, params)
#                 records = cursor.fetchall()
#         return records

#     def fetch_updated_ids_with_modified(
#             self, table: str, last_modified: str
#             ) -> List[Tuple[str, str]]:
#         """Получает id и modified обновленных записей для указанной таблицы."""
#         query = f"SELECT id, modified FROM content.{table} WHERE modified > %s ORDER BY modified LIMIT 100;"

#         return [
#             (record["id"], record["modified"])
#             for record in self.fetch_records(query, (last_modified,))
#         ]


#     def fetch_related_film_ids_with_modified(self, last_modified: str) -> List[Tuple[str, str]]:
#         """
#         Получает ID и modified фильмов, связанных с обновленными персонами или жанрами,
#         для последующего обновления данных в Elasticsearch.
#         """
#         # Получаем id и modified фильмов по изменённым персонам
#         person_query = """
#             SELECT fw.id, fw.modified
#             FROM content.film_work fw
#             LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id
#             WHERE pfw.person_id IN (
#                 SELECT id FROM content.person WHERE modified > %s
#             )
#             ORDER BY fw.modified
#             LIMIT 100;
#         """
#         films_by_person = [
#             (record["id"], record["modified"])
#             for record in self.fetch_records(person_query, (last_modified,))
#         ]

#         # Получаем id и modified фильмов по изменённым жанрам
#         genre_query = """
#             SELECT fw.id, fw.modified
#             FROM content.film_work fw
#             LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id
#             WHERE gfw.genre_id IN (
#                 SELECT id FROM content.genre WHERE modified > %s
#             )
#             ORDER BY fw.modified
#             LIMIT 100;
#         """
#         films_by_genre = [
#             (record["id"], record["modified"])
#             for record in self.fetch_records(genre_query, (last_modified,))
#         ]

#         # Объединяем результаты и убираем дубликаты по id, выбирая самую позднюю дату modified
#         film_dict = {}
#         for film_id, modified in films_by_person + films_by_genre:
#             if film_id not in film_dict or modified > film_dict[film_id]:
#                 film_dict[film_id] = modified

#         return list(film_dict.items())

#     def fetch_film_works_by_ids(self, ids: List[str]) -> List[Dict[str, Any]]:
#         """Получает полные данные для фильмов с указанными id."""
#         query = """
#             SELECT
#                 fw.id AS fw_id,
#                 fw.title,
#                 fw.description,
#                 fw.rating,
#                 fw.type,
#                 fw.created,
#                 fw.modified,
#                 pfw.role,
#                 p.id AS person_id,
#                 p.full_name,
#                 g.name AS genre
#             FROM content.film_work AS fw
#             LEFT JOIN content.person_film_work AS pfw ON pfw.film_work_id = fw.id
#             LEFT JOIN content.person AS p ON p.id = pfw.person_id
#             LEFT JOIN content.genre_film_work AS gfw ON gfw.film_work_id = fw.id
#             LEFT JOIN content.genre AS g ON g.id = gfw.genre_id
#             WHERE fw.id = ANY(%s);
#         """
#         return self.fetch_records(query, (ids,))

import requests
import logging
import json
from requests.exceptions import RequestException
from backoff import backoff
from config import (ES_HOST, INDEX_NAME,
                    INDEX_SETTINGS, ELASTIC_USER,
                    ELASTIC_PASSWORD)
from typing import List, Dict
from elasticsearch import Elasticsearch, exceptions


class ElasticSearchClient:
    def __init__(self):
        self.es = Elasticsearch(
            [ES_HOST],
            http_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
        )

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def create_index(self) -> None:
        """Создает индекс в Elasticsearch."""
        if not self.es.indices.exists(index=INDEX_NAME):
            try:
                response = self.es.indices.create(
                    index=INDEX_NAME,
                    body=INDEX_SETTINGS,
                    headers={"Content-Type": "application/json"},
                )
                logging.info(f"Индекс '{INDEX_NAME}' создан успешно: {response}")
            except exceptions.RequestError as e:
                logging.error(f"Ошибка при создании индекса в Elasticsearch: {e}")
                raise
        else:
            logging.info(f"Индекс '{INDEX_NAME}' уже существует.")

    @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
    def load_data(self, data: List[Dict[str, any]]) -> None:
        """Загружает данные в Elasticsearch с использованием bulk API."""
        bulk_data = ""
        for record in data:
            bulk_data += (
                '{"index": {"_index": "%s", "_id": "%s"}}\n' % (INDEX_NAME, record["id"])
            )
            bulk_data += json.dumps(record) + "\n"

        try:
            response = self.es.bulk(
                body=bulk_data,
                params={"filter_path": "items.*.error"},
            )
            if response["errors"]:
                logging.error(f"Ошибки при загрузке данных: {response}")
            else:
                logging.info(f"Загружено {len(data)} записей в индекс '{INDEX_NAME}'.")
        except exceptions.RequestError as e:
            logging.error(f"Ошибка при загрузке данных в Elasticsearch: {e}")
            raise


# class ElasticSearchClient:
#     def __init__(self, host=ES_HOST):
#         self.host = host

#     @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
#     def create_index(self) -> None:
#         try:
#             response = requests.head(f"{self.host}/{INDEX_NAME}")
#             if response.status_code == 404:
#                 response = requests.put(
#                     f"{self.host}/{INDEX_NAME}",
#                     json=INDEX_SETTINGS,
#                     headers={"Content-Type": "application/json"},
#                 )
#                 response.raise_for_status()
#                 logging.info(f"Индекс '{INDEX_NAME}' создан успешно.")
#             elif response.status_code == 200:
#                 logging.info(f"Индекс '{INDEX_NAME}' уже существует.")
#             else:
#                 response.raise_for_status()
#         except RequestException as e:
#             logging.error(f"Ошибка при создании индекса в Elasticsearch: {e}")
#             raise

#     @backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10)
#     def load_data(self, data: List[Dict[str, any]]) -> None:
#         """Загружает данные в Elasticsearch с использованием bulk API."""
#         bulk_data = ""
#         for record in data:
#             bulk_data += (
#                 json.dumps(
#                     {
#                         "index": {"_index": INDEX_NAME, "_id": record["id"]}
#                     }
#                 ) + "\n"
#             )
#             bulk_data += json.dumps(record) + "\n"

#         try:
#             response = requests.post(
#                 f"{self.host}/_bulk?filter_path=items.*.error",
#                 data=bulk_data,
#                 headers={"Content-Type": "application/x-ndjson"},
#             )
#             response.raise_for_status()
#             logging.info(f"Загружено {len(data)} записей в индекс '{INDEX_NAME}'.")
#         except RequestException as e:
#             logging.error(
#                 f"Ошибка при загрузке данных в Elasticsearch: {e}, не удалось загрузить записи: {response}"
#             )
#             raise

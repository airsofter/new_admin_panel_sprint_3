import json
from typing import List, Dict, Any, Generator
from elasticsearch import Elasticsearch, exceptions
from backoff import backoff
from config import (BORDER_SLEEP_TIME, ES_HOST, FACTOR, INDEX_NAME,
                    INDEX_SETTINGS, ELASTIC_USER,
                    ELASTIC_PASSWORD, CHUNK_SIZE, MAX_ATTEMPTS,
                    START_SLEEP_TIME)
from logging_config import logger


class ElasticSearchClient:
    def __init__(self):
        """Инициализирует клиента Elasticsearch."""
        self.es = Elasticsearch(
            [ES_HOST],
            http_auth=(ELASTIC_USER, ELASTIC_PASSWORD),
        )

    def _generate_chunks(
        self, data: List[Dict[str, Any]], chunk_size: int
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Генератор, разбивающий данные на чанки."""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    @backoff(
        start_sleep_time=START_SLEEP_TIME,
        factor=FACTOR,
        border_sleep_time=BORDER_SLEEP_TIME,
        max_attempts=MAX_ATTEMPTS,
    )
    def create_index(self) -> None:
        """Создает индекс в Elasticsearch."""
        if not self.es.indices.exists(index=INDEX_NAME):
            try:
                response = self.es.indices.create(
                    index=INDEX_NAME,
                    body=INDEX_SETTINGS,
                    headers={"Content-Type": "application/json"},
                )
                logger.info(f"Индекс '{INDEX_NAME}' создан успешно: {response}")
            except exceptions.RequestError as e:
                logger.error(f"Ошибка при создании индекса в Elasticsearch: {e}")
                raise
        else:
            logger.info(f"Индекс '{INDEX_NAME}' уже существует.")

    @backoff(
        start_sleep_time=START_SLEEP_TIME,
        factor=FACTOR,
        border_sleep_time=BORDER_SLEEP_TIME,
        max_attempts=MAX_ATTEMPTS,
    )
    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Загружает данные в Elasticsearch чанками."""
        logger.info(f"Всего записей для загрузки: {len(data)}")

        if not data:
            logger.warning("Передана пустая коллекция данных в Elasticsearch!")
            return

        for chunk in self._generate_chunks(data, CHUNK_SIZE):
            bulk_data = ""
            for record in chunk:
                bulk_data += '{"index": {"_index": "%s", "_id": "%s"}}\n' % (
                    INDEX_NAME,
                    record["id"],
                )
                bulk_data += json.dumps(record) + "\n"

            try:
                logger.info(f"Загрузка {len(chunk)} записей в индекс '{INDEX_NAME}'...")
                response = self.es.bulk(
                    body=bulk_data,
                    params={"filter_path": "items.*.error"},
                )

                errors_found = False
                for item in response.get("items", []):
                    if "error" in item.get("index", {}):
                        error = item["index"]["error"]
                        logger.error(
                            f"Ошибка при загрузке документа с ID {item['index']['_id']}:"
                            f"{error['reason']}"
                        )
                        errors_found = True

                if errors_found:
                    logger.error("Ошибки при загрузке данных в Elasticsearch.")
                else:
                    logger.info(
                        f"Успешно загружено {len(chunk)} записей в индекс '{INDEX_NAME}'."
                    )

            except exceptions.RequestError as e:
                logger.error(f"Ошибка при загрузке данных в Elasticsearch: {e}")
                raise
            except Exception as e:
                logger.error(
                    f"Неизвестная ошибка при загрузке данных в Elasticsearch: {e}"
                )
                raise

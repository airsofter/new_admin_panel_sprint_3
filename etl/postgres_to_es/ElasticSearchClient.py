import json
from typing import List, Dict, Any, Generator
from elasticsearch import Elasticsearch, exceptions
from backoff import backoff
from config import BACKOFF_CONFIG, ELASTIC_CONFIG, ETL_SETTINGS, INDEX_SETTINGS
from logging_config import logger


class ElasticSearchClient:
    def __init__(self) -> None:
        """Инициализирует клиент Elasticsearch."""
        es_config = ELASTIC_CONFIG.model_dump()
        self.es = Elasticsearch(
            [
                {
                    "host": es_config["host"],
                    "port": es_config["port"],
                    "scheme": es_config["method"],
                }
            ],
            http_auth=(es_config["user"], es_config["password"]),
        )

    def _generate_chunks(
        self, data: List[Dict[str, Any]], chunk_size: int
    ) -> Generator[List[Dict[str, Any]], None, None]:
        """Генератор, разбивающий данные на чанки."""
        for i in range(0, len(data), chunk_size):
            yield data[i:i + chunk_size]

    @backoff(**BACKOFF_CONFIG.model_dump())
    def create_index(self) -> None:
        """Создает индекс в Elasticsearch."""
        if not self.es.indices.exists(index=ELASTIC_CONFIG.index):
            try:
                response = self.es.indices.create(
                    index=ELASTIC_CONFIG.index,
                    body=INDEX_SETTINGS,
                    headers={"Content-Type": "application/json"},
                )
                logger.info(
                    f"Индекс '{ELASTIC_CONFIG.index}' создан успешно: {response}"
                )
            except exceptions.RequestError as e:
                logger.error(f"Ошибка при создании индекса в Elasticsearch: {e}")
                raise
        else:
            logger.info(f"Индекс '{ELASTIC_CONFIG.index}' уже существует.")

    @backoff(**BACKOFF_CONFIG.model_dump())
    def load_data(self, data: List[Dict[str, Any]]) -> None:
        """Загружает данные в Elasticsearch чанками."""
        logger.info(f"Всего записей для загрузки: {len(data)}")

        if not data:
            logger.warning("Передана пустая коллекция данных в Elasticsearch!")
            return

        for chunk in self._generate_chunks(data, ETL_SETTINGS.chunk_size):
            bulk_data = ""
            for record in chunk:
                bulk_data += '{"index": {"_index": "%s", "_id": "%s"}}\n' % (
                    ELASTIC_CONFIG.index,
                    record["id"],
                )
                bulk_data += json.dumps(record) + "\n"

            try:
                logger.info(
                    f"Загрузка {len(chunk)} записей в индекс '{ELASTIC_CONFIG.index}'..."
                )
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
                        f"Успешно загружено {len(chunk)} записей в индекс '{ELASTIC_CONFIG.index}'."
                    )

            except exceptions.RequestError as e:
                logger.error(f"Ошибка при загрузке данных в Elasticsearch: {e}")
                raise
            except Exception as e:
                logger.error(
                    f"Неизвестная ошибка при загрузке данных в Elasticsearch: {e}"
                )
                raise

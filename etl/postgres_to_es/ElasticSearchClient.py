import requests
import logging
from requests.exceptions import RequestException
from backoff import backoff
from postgres_to_es.config import INDEX_SETTINGS
from config import ES_HOST, INDEX_NAME


class ElasticSearchClient:
    def __init__(self, host=ES_HOST):
        self.host = host

    @backoff
    def create_index(self):
        try:
            response = requests.head(f"{self.host}/{INDEX_NAME}")
            if response.status_code == 404:
                response = requests.put(
                    f"{self.host}/{INDEX_NAME}",
                    json=INDEX_SETTINGS,
                    headers={"Content-Type": "application/json"},
                )
                response.raise_for_status()
                logging.info(f"Индекс '{INDEX_NAME}' создан успешно.")
            elif response.status_code == 200:
                logging.info(f"Индекс '{INDEX_NAME}' уже существует.")
            else:
                response.raise_for_status()
        except RequestException as e:
            logging.error(f"Ошибка при создании индекса в Elasticsearch: {e}")
            raise

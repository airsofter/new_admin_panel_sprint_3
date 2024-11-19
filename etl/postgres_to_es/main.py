import datetime
import logging
import time
from config import STATE_FILE_PATH
from Transformer import Transformer
from StateManager import StateManager, JsonFileStorage
from PostgresClient import PostgresClient
from ElasticSearchClient import ElasticSearchClient

logging.basicConfig(level=logging.INFO)


class Main:
    def __init__(self):
        self.pg_client = PostgresClient()
        self.es_client = ElasticSearchClient()
        self.transformer = Transformer()
        self.state_manager = StateManager(JsonFileStorage(STATE_FILE_PATH))
        self.state_manager.add_listener(
            lambda ids, table: self.es_client.load_data(
                self.transformer(self.tables[table][1](ids))
            )
        )
        self.es_client.create_index()

        self.tables = {
            "film_work": (
                self.pg_client.get_updated_film_ids,
                self.pg_client.get_film_details,
            ),
            "person": (
                self.pg_client.get_updated_person_ids,
                lambda ids: self.pg_client.get_film_details(
                    self.pg_client.get_film_ids_by_person_ids(ids)
                ),
            ),
            "genre": (
                self.pg_client.get_updated_genre_ids,
                lambda ids: self.pg_client.get_film_details(
                    self.pg_client.get_film_ids_by_genre_ids(ids)
                ),
            ),
        }

    def mainloop(self):
        while True:
            for table in self.tables:
                self.last_modified = self.state_manager.get_state() or datetime.datetime.strptime(
                    "1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S"
                )
                logging.info(f"Обрабатываем таблицу: {table}")

                now = datetime.datetime.now()
                self.state_manager.change_state(
                    self.last_modified, self.tables[table][0](self.last_modified), table
                )

                logging.info(f"Состояние обновлено для {table} до {self.last_modified}")
                self.last_modified = now

            time.sleep(10)


if __name__ == "__main__":
    Main().mainloop()

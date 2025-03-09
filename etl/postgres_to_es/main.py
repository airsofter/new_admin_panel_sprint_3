import datetime
import time
from config import STATE_FILE_PATH
from Transformer import Transformer
from StateManager import StateManager, JsonFileStorage
from PostgresClient import PostgresClient
from ElasticSearchClient import ElasticSearchClient
from logging_config import logger


time.sleep(60)


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
                lambda ids: self.pg_client.get_film_details(
                    ids
                ),
            ),
            "person": (
                self.pg_client.get_updated_person_ids,
                lambda ids: self.pg_client.get_film_details(
                    [film['id'] for film in self.pg_client.get_film_ids_by_person_ids(ids)]
                ),
            ),
            "genre": (
                self.pg_client.get_updated_genre_ids,
                lambda ids: self.pg_client.get_film_details(
                    [film['id'] for film in self.pg_client.get_film_ids_by_genre_ids(ids)]
                ),
            ),
        }

        self.last_modified_by_table = {
            table: self.state_manager.get_state(table)
            or datetime.datetime.strptime("1970-01-01 00:00:00", "%Y-%m-%d %H:%M:%S")
            for table in self.tables
        }

    def mainloop(self):
        while True:
            for table in self.tables:
                last_modified = self.last_modified_by_table[table]

                logger.info(
                    f"Обрабатываем таблицу: {table}, last_modified: {last_modified}"
                )

                now = datetime.datetime.now()
                updated_ids = list(self.tables[table][0](last_modified))

                if updated_ids and len(updated_ids) > 0:
                    self.state_manager.change_state(now, updated_ids, table)
                    self.last_modified_by_table[table] = now
                    logger.info(f"Состояние обновлено для {table} до {now}")
                else:
                    logger.info(f"Нет обновлений для {table}")

            time.sleep(10)


if __name__ == "__main__":
    Main().mainloop()

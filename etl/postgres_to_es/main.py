import time
import backoff
from PostgresClient import PostgresDB
from ElasticSearchClient import ElasticSearchClient
from Transformer import Transformer
from StateManager import StateManager


@backoff
def etl_process():
    state_manager = StateManager("state/state.json")
    last_processed_id = state_manager.get_state("last_processed_id", 0)

    postgres = PostgresDB()
    elastic = ElasticSearchClient()

    while True:
        movies = postgres.fetch_movies(last_processed_id)
        if not movies:
            time.sleep(10)
            continue

        transformed_data = [Transformer.transform(movie) for movie in movies]
        elastic.bulk_insert(transformed_data)

        last_processed_id = movies[-1]["id"]
        state_manager.save_state("last_processed_id", last_processed_id)


if __name__ == "__main__":
    etl_process()

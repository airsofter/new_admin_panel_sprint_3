from pydantic_settings import BaseSettings
from pydantic import Field

from typing import Any, Dict


class PostgresLocal(BaseSettings):
    host: str = "127.0.0.1"
    port: int = 5432
    dbname: str = "theatre"
    user: str = Field(..., alias="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASSWORD")


class PostgresProd(BaseSettings):
    host: str = Field(..., alias="SQL_HOST")
    port: int = Field(..., alias="SQL_PORT")
    dbname: str = Field(..., alias="POSTGRES_DB")
    user: str = Field(..., alias="POSTGRES_USER")
    password: str = Field(..., alias="POSTGRES_PASSWORD")


class ElasticConfig(BaseSettings):
    host: str = Field(..., alias="ES_HOST")
    port: int = Field(..., alias="ES_PORT")
    user: str = Field(..., alias="ELASTIC_USER")
    password: str = Field(..., alias="ELASTIC_PASSWORD")
    method: str = "http"
    index: str = "movies"


class BackoffConfig(BaseSettings):
    start_sleep_time: float = 0.1
    max_attempts: int = 10
    border_sleep_time: float = 10
    factor: float = 2


class ETLSettings(BaseSettings):
    batch_size: int = 100
    state_file_path: str = "state/state.json"
    chunk_size: int = 100


POSTGRES_LOCAL = PostgresLocal()
POSTGRES_PROD = PostgresProd()
ELASTIC_CONFIG = ElasticConfig()
BACKOFF_CONFIG = BackoffConfig()
ETL_SETTINGS = ETLSettings()


INDEX_SETTINGS: Dict[str, Any] = {
        "settings": {
            "refresh_interval": "1s",
            "analysis": {
                "filter": {
                    "english_stop": {"type": "stop", "stopwords": "_english_"},
                    "english_stemmer": {"type": "stemmer", "language": "english"},
                    "english_possessive_stemmer": {
                        "type": "stemmer",
                        "language": "possessive_english",
                    },
                    "russian_stop": {"type": "stop", "stopwords": "_russian_"},
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                },
                "analyzer": {
                    "ru_en": {
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "english_stop",
                            "english_stemmer",
                            "english_possessive_stemmer",
                            "russian_stop",
                            "russian_stemmer",
                        ],
                    }
                },
            },
        },
        "mappings": {
            "dynamic": "strict",
            "properties": {
                "id": {"type": "keyword"},
                "imdb_rating": {"type": "float"},
                "genres": {"type": "keyword"},
                "title": {
                    "type": "text",
                    "analyzer": "ru_en",
                    "fields": {"raw": {"type": "keyword"}},
                },
                "description": {"type": "text", "analyzer": "ru_en"},
                "directors_names": {"type": "text", "analyzer": "ru_en"},
                "actors_names": {"type": "text", "analyzer": "ru_en"},
                "writers_names": {"type": "text", "analyzer": "ru_en"},
                "directors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "actors": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
                "writers": {
                    "type": "nested",
                    "dynamic": "strict",
                    "properties": {
                        "id": {"type": "keyword"},
                        "name": {"type": "text", "analyzer": "ru_en"},
                    },
                },
            },
        },
    }

from typing import List, Dict, Any
import logging


class Transformer:
    def __init__(self):
        self.transformed_data = []

    def __call__(self, films: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Преобразует данные о фильмах в формат, подходящий для загрузки в Elasticsearch."""
        self.transformed_data = []
        print("            aaaaaaaaaaaa", films)
        for film in films:
            transformed_film = self._transform_film(film)
            self.transformed_data.append(transformed_film)
        return self.transformed_data

    def _transform_film(self, film: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразует отдельный фильм в нужный формат для Elasticsearch."""
        transformed = {
            "id": film["fw_id"],
            "title": film["title"],
            "description": film["description"],
            "imdb_rating": film["rating"],
            "genres": list(film["genres"]),
            "directors_names": ", ".join(film["directors"]),
            "actors_names": ", ".join(film["actors"]),
            "writers_names": ", ".join(film["writers"]),
            "directors": self._transform_people(film["directors"]),
            "actors": self._transform_people(film["actors"]),
            "writers": self._transform_people(film["writers"]),
        }
        return transformed

    def _transform_people(self, people: List[str]) -> List[Dict[str, Any]]:
        """Преобразует список имен людей в формат, подходящий для Elasticsearch (с ID и именем)."""
        return [{"id": person.strip(), "name": person.strip()} for person in people]

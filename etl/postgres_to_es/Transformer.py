from typing import List, Dict, Any, Tuple


class Transformer:
    def __call__(self, films: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Преобразует данные о фильмах в формат, подходящий для загрузки в Elasticsearch."""
        grouped_films = self._group_films_by_id(films)
        transformed_data = [self._transform_film(film) for film in grouped_films]
        return transformed_data

    def _group_films_by_id(self, films: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Группирует фильмы по fw_id, собирая информацию о людях по ролям."""
        film_dict = {}

        for film in films:
            fw_id = film["fw_id"]
            if fw_id not in film_dict:
                film_dict[fw_id] = {
                    "id": fw_id,
                    "title": film["title"],
                    "description": film["description"],
                    "imdb_rating": film["rating"],
                    "genres": set(),
                    "directors": set(),
                    "actors": set(),
                    "writers": set(),
                }

            # Добавляем жанры
            if film["genre_name"]:
                film_dict[fw_id]["genres"].add(film["genre_name"])

            # Распределяем людей по ролям
            person_info = (film["person_id"], film["person_name"])
            if film["role"] == "director":
                film_dict[fw_id]["directors"].add(person_info)
            elif film["role"] == "actor":
                film_dict[fw_id]["actors"].add(person_info)
            elif film["role"] == "writer":
                film_dict[fw_id]["writers"].add(person_info)

        # Преобразуем множества в списки
        for film in film_dict.values():
            film["genres"] = list(film["genres"])
            film["directors"] = list(film["directors"])
            film["actors"] = list(film["actors"])
            film["writers"] = list(film["writers"])

        return list(film_dict.values())

    def _transform_film(self, film: Dict[str, Any]) -> Dict[str, Any]:
        """Преобразует отдельный фильм в нужный формат для Elasticsearch."""
        transformed_film = {
            "id": str(film["id"]),
            "title": film["title"],
            "description": film["description"],
            "imdb_rating": film["imdb_rating"],
            "genres": film["genres"],
            "directors_names": [name for _, name in film["directors"]],
            "actors_names": [name for _, name in film["actors"]],
            "writers_names": [name for _, name in film["writers"]],
            "directors": self._transform_people(film["directors"]),
            "actors": self._transform_people(film["actors"]),
            "writers": self._transform_people(film["writers"]),
        }

        return transformed_film

    def _transform_people(self, people: List[Tuple[str, str]]) -> List[Dict[str, str]]:
        """Преобразует список имен людей в формат, подходящий для Elasticsearch (с ID и именем)."""
        return [{"id": str(person_id), "name": name} for person_id, name in people]

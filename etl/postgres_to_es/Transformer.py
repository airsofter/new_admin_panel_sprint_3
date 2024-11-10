class Transformer:
    @staticmethod
    def transform(movie):
        return {
            "_index": "movies",
            "_id": movie["id"],
            "_source": {
                "title": movie["title"],
                "description": movie["description"],
                "imdb_rating": movie["imdb_rating"],
                "genres": movie["genres"],
            },
        }

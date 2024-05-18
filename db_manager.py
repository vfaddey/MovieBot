import psycopg2
import psycopg2.extras


class DatabaseManager:
    def __init__(self, conn):
        self.conn = conn

    def get_film_by_name(self, name: str):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT movies.*, countries.name AS country_name, ratings.*, array_agg(genres.name) AS genres
                    FROM movies
                    JOIN countries ON movies.country_id = countries.country_id
                    JOIN ratings ON movies.rating_id = ratings.id
                    JOIN movie_genre ON movies.id = movie_genre.movie_id
                    JOIN genres ON movie_genre.genre_id = genres.genre_id
                    WHERE movies.name ILIKE %s
                    GROUP BY movies.id, countries.name, ratings.id
                    LIMIT 1
                """, (f'%{name}%',))
        film = cur.fetchone()
        cur.close()
        return film

    def get_films_with_rating(self, min_rating: float, count=5):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
            SELECT movies.*, countries.name AS country_name, ratings.kp AS rating, array_agg(genres.name) AS genres
            FROM movies
            JOIN countries ON movies.country_id = countries.country_id
            JOIN ratings ON movies.rating_id = ratings.id
            JOIN movie_genre ON movies.id = movie_genre.movie_id
            JOIN genres ON movie_genre.genre_id = genres.genre_id
            WHERE ratings.kp >= %s
            GROUP BY movies.id, countries.name, ratings.id
            ORDER BY ratings.kp DESC
            LIMIT %s
        """, (min_rating, count))
        films = cur.fetchall()
        cur.close()
        return films

    def get_films_by_genre(self, genre: str, count=5):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT movies.*, countries.name AS country_name, ratings.kp AS rating, array_agg(genres.name) AS genres
                    FROM movies
                    JOIN countries ON movies.country_id = countries.country_id
                    JOIN ratings ON movies.rating_id = ratings.id
                    JOIN movie_genre ON movies.id = movie_genre.movie_id
                    JOIN genres ON movie_genre.genre_id = genres.genre_id
                    WHERE genres.name ILIKE %s
                    GROUP BY movies.id, countries.name, ratings.id
                    ORDER BY movies.name
                    LIMIT %s
                """, (f'%{genre}%', count))
        films = cur.fetchall()
        cur.close()
        return films

    def get_films_for_age(self, age: int, count=5):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT movies.*, countries.name AS country_name, ratings.kp AS rating, array_agg(genres.name) AS genres
                    FROM movies
                    JOIN countries ON movies.country_id = countries.country_id
                    JOIN ratings ON movies.rating_id = ratings.id
                    JOIN movie_genre ON movies.id = movie_genre.movie_id
                    JOIN genres ON movie_genre.genre_id = genres.genre_id
                    WHERE movies.age_rating <= %s
                    GROUP BY movies.id, countries.name, ratings.id
                    ORDER BY movies.name
                    LIMIT %s
                """, (age, count))
        films = cur.fetchall()
        cur.close()
        return films

    def get_films_by_country(self, country: str, count=5):
        cur = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute("""
                    SELECT movies.name, ratings.kp AS rating
                    FROM movies
                    JOIN countries ON movies.country_id = countries.country_id
                    JOIN ratings ON movies.rating_id = ratings.id
                    WHERE countries.name ILIKE %s
                    ORDER BY ratings.kp DESC
                    LIMIT %s
                """, (f'%{country}%', count))
        films = cur.fetchall()
        cur.close()
        return films


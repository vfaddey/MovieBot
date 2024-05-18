import json
import pprint
import psycopg2
from dataclasses import dataclass

conn = psycopg2.connect(
    dbname="films",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)


@dataclass
class Movie:
    name: str
    year: int
    country: str
    description: str
    movie_length: int
    genre: [str]
    age_rating: int
    poster_url: str
    short_description: str
    ratings: dict


def add_rating(cur, ratings):
    cur.execute("""
        INSERT INTO ratings (film_critics, imdb, kp, russian_film_critics)
        VALUES (%s, %s, %s, %s)
        RETURNING id
    """, (
        ratings.get('filmCritics'),
        ratings.get('imdb'),
        ratings.get('kp'),
        ratings.get('russianFilmCritics')
    ))
    return cur.fetchone()[0]


def get_or_create_country(cur, country_name):
    cur.execute("""
        SELECT country_id FROM countries WHERE name = %s
    """, (country_name,))
    country_id = cur.fetchone()
    if not country_id:
        cur.execute("""
            INSERT INTO countries (name) VALUES (%s)
            RETURNING country_id
        """, (country_name,))
        return cur.fetchone()[0]
    return country_id[0]


def add_movie(cur, movie, country_id, rating_id):
    cur.execute("""
        INSERT INTO movies (name, year, country_id, description, movie_length, age_rating, poster_url, short_description, rating_id)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id
    """, (
        movie.name,
        movie.year,
        country_id,
        movie.description,
        movie.movie_length,
        movie.age_rating,
        movie.poster_url,
        movie.short_description,
        rating_id
    ))
    return cur.fetchone()[0]


def get_or_create_genre(cur, genre_name):
    cur.execute("""
        SELECT genre_id FROM genres WHERE name = %s
    """, (genre_name,))
    genre_id = cur.fetchone()
    if not genre_id:
        cur.execute("""
            INSERT INTO genres (name) VALUES (%s)
            RETURNING genre_id
        """, (genre_name,))
        return cur.fetchone()[0]
    return genre_id[0]


def link_movie_genre(cur, movie_id, genre_id):
    cur.execute("""
        INSERT INTO movie_genre (movie_id, genre_id) VALUES (%s, %s)
    """, (movie_id, genre_id))


def add_to_db(movie: Movie):
    cur = conn.cursor()

    rating_id = add_rating(cur, movie.ratings)

    country_id = get_or_create_country(cur, movie.country)

    movie_id = add_movie(cur, movie, country_id, rating_id)

    for genre_name in movie.genre:
        genre_id = get_or_create_genre(cur, genre_name)
        link_movie_genre(cur, movie_id, genre_id)

    conn.commit()
    cur.close()


with open('films.json', 'r', encoding='utf-8') as file:
    movies = json.load(file)

for movie in movies:
    name = movie['name']
    year = movie['year']
    country = movie['countries'][0]['name']
    age_rating = movie['ageRating']
    description = movie['description']
    genres = [x['name'] for x in movie['genres']]
    poster = movie['poster']['url']
    rating = movie['rating']
    length = movie['movieLength']
    short_description = movie['shortDescription']
    obj_Movie = Movie(name, year, country, description, length, genres, age_rating, poster, short_description, rating)
    add_to_db(obj_Movie)

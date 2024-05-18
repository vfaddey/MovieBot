import requests
import json

response = requests.get('https://api.kinopoisk.dev/v1.4/movie?rating.kp=7-10&type=movie&limit=150',
                        headers={'X-API-KEY': 'API-KEY'}).json()['docs']

with open('films.json', 'w', encoding='utf-8') as file:
    array = []
    for movie in response:
        if movie['name'] is not None:
            array.append(movie)
    json.dump(array, file)



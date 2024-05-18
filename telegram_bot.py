from telebot import TeleBot
from telebot import types
from db_manager import DatabaseManager
import psycopg2
from command_handler import CommandHandler

bot = TeleBot('API-KEY')

conn = psycopg2.connect(
    dbname="films",
    user="postgres",
    password="123",
    host="localhost",
    port="5432"
)

db_manager = DatabaseManager(conn)


def main_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('Поиск по жанру')
    btn2 = types.KeyboardButton('Поиск по имени')
    btn3 = types.KeyboardButton('Поиск по стране')
    btn4 = types.KeyboardButton('Поиск по рейтингу')
    btn5 = types.KeyboardButton('Поиск по возрастному ограничению')
    markup.add(btn1, btn2, btn3, btn4, btn5)
    return markup


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 'Привет! Я бот для поиска фильмов.', reply_markup=main_keyboard())


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text
    if command_handler.has_command(text):
        command_handler.get_command(text)(message.chat.id)
    else:
        bot.send_message(message.chat.id, 'Выберите команду из списка.')


def search_movie_by_name(message):
    name = message.text
    film = db_manager.get_film_by_name(name)
    if film:
        send_film_info(message.chat.id, film)
    else:
        bot.send_message(message.chat.id, "Фильм с указанным названием не найден.", reply_markup=main_keyboard())


def search_by_genre(message):
    genre = message.text
    films = db_manager.get_films_by_genre(genre, count=5)
    if films:
        markup = types.InlineKeyboardMarkup()
        for film in films:
            btn = types.InlineKeyboardButton(f"{film['name']} - {film['rating']}", callback_data=f"film_{film['name']}")
            markup.add(btn)
        film_list = "\n".join([f"{film['name']} - {film['rating']}" for film in films])
        bot.send_message(message.chat.id, f"Найдены фильмы:\n{film_list}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Фильмы по указанному жанру не найдены.", reply_markup=main_keyboard())


def search_by_country(message):
    country = message.text
    films = db_manager.get_films_by_country(country, count=5)
    if films:
        markup = types.InlineKeyboardMarkup()
        for film in films:
            btn = types.InlineKeyboardButton(f"{film['name']} - {film['rating']}", callback_data=f"film_{film['name']}")
            markup.add(btn)
        film_list = "\n".join([f"{film['name']} - {film['rating']}" for film in films])
        bot.send_message(message.chat.id, f"Найдены фильмы:\n{film_list}", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Фильмы по указанной стране не найдены.", reply_markup=main_keyboard())


def search_by_age(message):
    try:
        age = int(message.text)
        films = db_manager.get_films_for_age(age, count=5)
        if films:
            markup = types.InlineKeyboardMarkup()
            for film in films:
                btn = types.InlineKeyboardButton(f"{film['name']} - {film['rating']}",
                                                 callback_data=f"film_{film['name']}")
                markup.add(btn)
            film_list = "\n".join([f"{film['name']} - {film['rating']}" for film in films])
            bot.send_message(message.chat.id, f"Найдены фильмы:\n{film_list}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Фильмы для указанного возрастного ограничения не найдены.",
                             reply_markup=main_keyboard())
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число.", reply_markup=main_keyboard())


def search_by_rating(message):
    try:
        rating = float(message.text)
        films = db_manager.get_films_with_rating(rating, count=5)
        if films:
            markup = types.InlineKeyboardMarkup()
            for film in films:
                btn = types.InlineKeyboardButton(f"{film['name']} - {film['rating']}", callback_data=f"film_{film['name']}")
                markup.add(btn)
            film_list = "\n".join([f"{film['name']} - {film['rating']}" for film in films])
            bot.send_message(message.chat.id, f"Найдены фильмы:\n{film_list}", reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Фильмы с указанным рейтингом не найдены.", reply_markup=main_keyboard())
    except ValueError:
        bot.send_message(message.chat.id, "Пожалуйста, введите корректное число.", reply_markup=main_keyboard())


@bot.callback_query_handler(func=lambda call: call.data.startswith('film_'))
def handle_film_callback(call):
    film_name = call.data[5:]
    film = db_manager.get_film_by_name(film_name)
    if film:
        send_film_info(call.message.chat.id, film)


def send_film_info(chat_id, film):
    poster_url = film.get('poster_url', '')
    caption = (f"*Название:* {film['name']}\n"
               f"*Год выпуска:* {film['year']}\n"
               f"*Страна:* {film['country_name']}\n"
               f"*Описание:* {film['description']}\n"
               f"*Длительность:* {film['movie_length']} минут\n"
               f"*Возрастной рейтинг:* {film['age_rating']}\n"
               f"*Краткое описание:* {film['short_description']}\n"
               f"*Рейтинги:*\n"
               f"  Ожидание: {film['film_critics']}\n"
               f"  Критики: {film['imdb']}\n"
               f"  IMDb: {film['kp']}\n"
               f"  Кинопоиск: {film['russian_film_critics']}\n"
               f"*Жанры:* {', '.join(film['genres'])}")
    bot.send_photo(chat_id, poster_url, caption=caption, parse_mode='Markdown')


def ask_name(chat_id):
    answer = bot.send_message(chat_id, 'Введите название фильма')
    bot.register_next_step_handler(answer, search_movie_by_name)


def ask_genre(chat_id):
    answer = bot.send_message(chat_id, 'Введите жанр')
    bot.register_next_step_handler(answer, search_by_genre)


def ask_country(chat_id):
    answer = bot.send_message(chat_id, 'Введите страну')
    bot.register_next_step_handler(answer, search_by_country)


def ask_rating(chat_id):
    answer = bot.send_message(chat_id, 'Введите минимальный рейтинг')
    bot.register_next_step_handler(answer, search_by_rating)


def ask_age(chat_id):
    answer = bot.send_message(chat_id, 'Введите возрастное ограничение (только число)')
    bot.register_next_step_handler(answer, search_by_age)


commands = {
    'Поиск по имени': ask_name,
    'Поиск по жанру': ask_genre,
    'Поиск по стране': ask_country,
    'Поиск по рейтингу': ask_rating,
    'Поиск по возрастному ограничению': ask_age
}

command_handler = CommandHandler(commands)

bot.polling()

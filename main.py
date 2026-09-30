import telebot
from logic import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests

bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, """Добро пожаловать! Чтобы зарегистрировать команду, введите /register
Для просмотра рейтинга введи: /rating
Для просмотра вопросов: /questions""")


@bot.message_handler(commands=['register'])
def register(message):
    markup = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    markup.add(KeyboardButton('Да'), KeyboardButton("Нет"))
    bot.send_message(message.chat.id, "У вас уже есть команда?", reply_markup=markup)
    bot.register_next_step_handler(message,register_step1)


def register_step1(message):
    teams = manager.get_teams_name()
    if message.text == "Да" and teams:
        bot.send_message(message.chat.id, 'Выберите название команды: ', reply_markup=gen_teams_markup(teams))
    else: 
        bot.send_message(message.chat.id, "Введите название команды: ")
        bot.register_next_step_handler(message,register_step3)


def register_step3(message):
    team_id = manager.insert_team(message.text)
    manager.insert_user(message.chat.id, team_id)
    register_step4(message)


def register_step4(message):
    bot.send_message(message.chat.id, "Вы зарегистрированы. Начнем квиз!")
    bot.send_message(message.chat.id, """Прежде чем начать, небольшая инструкция:

Сегодня тебе предстоит потренироваться в написании SQL-запросов для получения данных. Используй для этого расширение в VScode 'SQLite3 Editor'
Базу данных, из которой ты будешь получать данные, отправляю ниже ⬇️⬇️⬇️""")
    with open('world_information.db', 'rb') as file:
        bot.send_document(message.chat.id, file)
    bot.send_message(message.chat.id, "Это база данных с информацией о странах. В ней есть три таблицы: таблица с континентами, странами и информацией о странах. Все таблицы связаны между собой. Если у тебя возникнут вопросы - задавай их преподавталею 😉")
    bot.send_message(message.chat.id, "Удачи! У тебя все получится🔥")
    bot.send_message(message.chat.id, "Введи команду /questions и посмотри доступные вопросы!")


@bot.message_handler(commands=['rating'])
def get_rating(message):
    rating = manager.get_rating() 
    bot.send_message(message.chat.id, 'Рейтинг команд (место, название команды, очки):', reply_markup=gen_rating_markup(rating))


@bot.message_handler(commands=['questions'])
def get_questions_handler(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, 'Список вопросов', reply_markup=gen_questions_markup(manager.get_answers(chat_id))) 


if __name__ == '__main__':
    manager = DB_Manager(DATABASE)
    bot.polling()

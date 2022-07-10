from random import randrange
from pprint import pprint as pp
import re
import json
import datetime

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from search_people import test_search_results
from Database import Postgresql


class Server:

    def __init__(self, api_token, group_id, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        self.vk_api = self.vk.get_api()

    def send_msg(self, user_id: int, message: str, keyboard=None):
        """Отправка сообщения пользователю"""
        if keyboard != None:
            self.vk_api.messages.send(peer_id=user_id, message=message,
                                      keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))
        else:
            self.vk_api.messages.send(peer_id=user_id, message=message, random_id=randrange(10 ** 7))

    def send_img(self, user_id: int, img: str, keyboard=None):
        """Отправка фотографий пользователю"""
        if keyboard != None:
            self.vk_api.messages.send(peer_id=user_id, attachment=img,
                                      keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))
        else:
            self.vk_api.messages.send(peer_id=user_id, attachment=img, random_id=randrange(10 ** 7))

    def delete_buttons(self, user_id: int, message: str):
        """Убираем кнопки из разговора"""
        kb = {"one_time": True, "buttons": []}
        self.vk_api.messages.send(peer_id=user_id, message=message,
                                  keyboard=json.dumps(kb), random_id=randrange(10 ** 7))

    def say_hello(self, user_id: int, text_message: str):
        """Ищем приветствие в сообщении. Если оно есть - приветствуем пользователя в ответ"""
        pattern = r"[П/п]ривет|[З|з]дравствуй[\w]*|[H|h]ello|[Х|х]ай|[Д|д]обр[а-я]+ (утро|день|вечер)"
        result = re.findall(pattern, text_message)
        if len(result) != 0:
            user_name = self.vk_api.users.get(user_id=user_id)[0]['first_name']
            hello_message = f"Привет, {user_name}"
            self.send_msg(user_id, hello_message)

    def start_conversation(self, user_id: int):
        """Предлагаем пользователю начать поиск людей"""
        message = "Хотите начать поиск людей для знакомств?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.PRIMARY, payload={"type": "yes_search"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.PRIMARY, payload={"type": "no_search"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Понравившиеся", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "show_favorites"})
        self.send_msg(user_id, message, keyboard)

    def start_seacrh_person(self):
        pass

    def get_user_info(self, user_id: int) -> dict:
        """Собираем информацию о пользователе"""
        result = self.vk_api.users.get(user_id=user_id, fields="bdate,city,relation,sex")
        # Получаем информацию о дне рождении, городе, статусе отношений и пол
        db = Postgresql()
        if not db.query(f"SELECT id FROM initiators WHERE id = {user_id}"):
            db.insert_initiator(user_id)
        if "bdate" in result[0]:
            user_birthday = result[0]["bdate"]
            age = self.get_age(user_birthday)
        else:
            age = "не указан"
        if "city" in result[0]:
            city = result[0]["city"]  # city - словарь, где ключи id и title
        else:
            city = "не указан"
        if result[0]["sex"] == 0:
            gender = "не указан"
        else:
            gender = result[0]["sex"]

        user_info = {"user_id": user_id, "first_name": result[0]["first_name"], "last_name": result[0]["last_name"],
                     "age": age, "city": city, "gender": gender}
        return user_info

    def get_age(self, birthday: str) -> int:
        """Вычисляем возраст пользователя"""
        current_date = datetime.date.today()
        birthday = birthday.split(".")
        birthday = datetime.date(year=int(birthday[2]), month=int(birthday[1]), day=int(birthday[0]))
        age = int((current_date - birthday).days / 365)
        return age

    def analys_user_info(self, user_info: dict) -> bool:
        """Смотрим, указаны ли у пользователя все ключевые поля в профиле"""
        if user_info['age'] == "не указан" or user_info['city'] == "не указан" or user_info['gender'] == "не указан":
            error_message = f"У вас не указаны некоторые параметры:\n\n" \
                            f"День рождения: {user_info['age']}\n" \
                            f"Город: {user_info['city']}\n" \
                            f"Пол: {user_info['gender']}\n\n" \
                            f"Увы, но без полной информации нельзя будет продолжить поиск."
            self.send_msg(user_info['user_id'], error_message)
            user_info_data = False
        else:
            user_info_data = True
        return user_info_data

    def ask_age(self, user_id: int) -> int:
        """Запрашиваем возраст людей, которых будем искать"""
        age = None
        ask_message = "Возраст:"
        self.delete_buttons(user_id, ask_message)
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_text = event.object.message['text']
                try:
                    age = int(user_text)
                except ValueError:
                    correct_age = "Не понял вас. Напишите возраст цифрами:"
                    self.send_msg(user_id, correct_age)
                if type(age) == int:
                    break
        return age

    def ask_gender(self, user_id: int) -> int:
        """Запрашиваем пол людей, которых будем искать"""
        gender = 0
        ask_gender = "Кого будем искать?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label="Девушку", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label="Парня", color=VkKeyboardColor.PRIMARY)
        self.send_msg(user_id, ask_gender, keyboard)
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_text = event.object.message['text']
                if user_text == "Девушку":
                    gender = 1
                    break
                elif user_text == "Парня":
                    gender = 2
                    break
        return gender

    def ask_user_for_search(self, user_info: dict) -> dict:
        """Спрашиваем, верны ли данные для поиска"""
        user_id = user_info["user_id"]
        who = ""
        gender = 0
        if user_info["gender"] == 1:
            who = "парня"
            gender = 2
        elif user_info["gender"] == 2:
            who = "девушку"
            gender = 1

        search_parameters = {"age": user_info['age'], "gender": gender, "city": user_info['city']['id']}

        message = f"{user_info['first_name']}, будем искать {who} в возрасте {user_info['age']} лет из г. {user_info['city']['title']}, верно?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "start_search"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "get_new_info_for_search"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Стоп! Я передумал", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "stop"})
        self.send_msg(user_info["user_id"], message, keyboard)
        return search_parameters

    def get_new_info_for_search(self, user_id: int) -> dict:
        """Формируем новые параметры для поиска"""
        message = "Хорошо. Задайте параметры для поиска."
        self.delete_buttons(user_id, message)
        gender = self.ask_gender(user_id)
        age = self.ask_age(user_id)
        result = self.vk_api.users.get(user_id=user_id, fields="city")
        city = result[0]['city']['id']
        search_parameters = {"age": age, "gender": gender, "city": city}
        return search_parameters

    def buttons_like_dislike(self) -> object:
        """Кнопки LIKE, DISLIKE и STOP для показа результатов поиска пользователю"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label="LIKE", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label="DISLIKE", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label="Стоп! Хватит!", color=VkKeyboardColor.SECONDARY)
        return keyboard

    def show_results(self, user_id, search_result=None):
        people = []

        # result будет примерно таким:
        # result = {"id": id, "first_name": first_name, "last_name": last_name, "profile": link, "photos": photos str}

        # for result in search_result:
        # проверяем, есть ли id человека в базе лайков и дизлайков у текущего юзера
        # да - пропускаем, берем слудующий
        # нет, добавляем в people[]

        favorites = []
        black_list = []

        # тестовые данные:
        photos = "photo716417153_457239020,photo716417153_457239018,photo716417153_457239019"
        show = True
        db = Postgresql()
        for result in test_search_results:
            if not db.query(f"SELECT id FROM founds WHERE id = {result['id']}"):
                db.insert_found(result)
                if show == True:
                    result_msg = f"{result['first_name']} {result['last_name']}\nпрофиль: {result['profile']}"
                    self.delete_buttons(user_id, result_msg)
                    keyboard = self.buttons_like_dislike()
                    self.send_img(user_id, photos, keyboard)
                    for event in self.long_poll.listen():
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            user_text = event.object.message['text']
                            if user_text == "LIKE":
                                db.insert_favourite(user_id, result['id'])
                                # favorites.append(result)
                                break
                            elif user_text == "DISLIKE":
                                db.insert_dislike(user_id, result['id'])
                                # black_list.append(result)
                                break
                            elif user_text == "Стоп! Хватит!":
                                goodbye_msg = "Хорошо, до новых встреч!"
                                self.delete_buttons(user_id, goodbye_msg)
                                favorites_message = "Хотите еще раз взглянуть на тех, кто вам понравился?"
                                kb = VkKeyboard(one_time=True)
                                kb.add_callback_button(label="Да", color=VkKeyboardColor.SECONDARY,
                                                       payload={"type": "show_favorites"})
                                kb.add_line()
                                kb.add_callback_button(label="Нет", color=VkKeyboardColor.SECONDARY,
                                                       payload={"type": "no_search"})
                                self.send_msg(user_id, favorites_message, kb)
                                show = False
                                break
                else:
                    break
        # либо список результатов закончился, либо пользователь остановил показ
        # если показ остановлен, т.е. если show False: мы должны обновить базу лайков и дизлайков текущего пользователя
        # если show True, то нужно получить новые (следующий массив) результаты и снова показывать их
        # new_result = vk_search_people
        # show_results(new_results)
        # return favorites

    # def show_favorites(self, user_id: int, favorites):
    #     if len(favorites) == 0:
    #         message = "Увы, список понравившихся людей пуст.\nМожет быть стоит сначала кого-нибудь найти и посмотреть?"
    #         self.delete_buttons(user_id, message)
    #     else:
    #         message = "Понравившиеся:"
    #         self.delete_buttons(user_id, message)
    #         for person in favorites:
    #             person_info = f"{person['first_name']} {person['last_name']}: {person['profile']}"
    #             self.send_msg(user_id, person_info)

    def show_favorites(self, user_id: int):
        db = Postgresql()
        select = f"SELECT id, first_name, last_name, profile FROM founds JOIN favourites f ON founds.id = f.found_id WHERE f.initiator_id = {user_id}"
        if not db.query(select):
            message = "Увы, список понравившихся людей пуст.\nМожет быть стоит сначала кого-нибудь найти и посмотреть?"
            self.delete_buttons(user_id, message)
        else:
            message = "Понравившиеся:"
            self.delete_buttons(user_id, message)
            for person in db.query(select):
                person_info = f"{person[1]} {person[2]}: {person[3]}"
                self.send_msg(user_id, person_info)

    def start(self):
        """Отслеживаем события в чате, общаемся с пользователем"""
        favorites = []
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.object.message['from_id']
                user_text = event.object.message['text']
                self.say_hello(user_id, user_text)
                self.start_conversation(user_id)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                user_id = event.object['user_id']
                if event.object.payload.get("type") == "yes_search":
                    user_info = self.get_user_info(user_id)
                    result = self.analys_user_info(user_info)
                    if result == False:
                        message = "Пожалуйста, обновите свой профиль и возвращайтесь!"
                        self.send_msg(user_id, message)
                    else:
                        search_parameters = self.ask_user_for_search(user_info)
                elif event.object.payload.get("type") == "no_search":
                    new_message = "Нет, так нет. Как-нибудь в другой раз. До скорой встречи!"
                    self.delete_buttons(user_id, new_message)
                elif event.object.payload.get("type") == "stop":
                    new_message = "Очень жаль. Когда передумаете еще раз, обращайтесь!"
                    self.delete_buttons(user_id, new_message)
                elif event.object.payload.get("type") == "start_search":
                    new_message = "Отлично, погнали!"
                    self.delete_buttons(user_id, new_message)
                    # search_result = vk_search_people(search_parameters)
                    search_result = None  # убрать, для теста
                    favorites = self.show_results(user_id, search_result)
                elif event.object.payload.get("type") == "get_new_info_for_search":
                    search_parameters = self.get_new_info_for_search(user_id)
                    # search_result = vk_search_people(search_parameters)
                    search_result = None  # убрать, для теста
                    favorites = self.show_results(user_id, search_result)
                elif event.object.payload.get("type") == "show_favorites":
                    # показать список лайков
                    self.show_favorites(user_id)

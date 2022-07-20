import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from search_people import search_people, get_user_info, analysis_user_info
from sql_database import Postgresql

from random import randrange
import re
import json


class Server:

    def __init__(self, api_token, group_id, server_name: str = "Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        self.vk_api = self.vk.get_api()
        self.db = Postgresql()

    def send_msg(self, user_id: int, message=None, attachment=None, keyboard=None):
        """Отправка сообщения пользователю"""
        if keyboard is not None:
            self.vk_api.messages.send(peer_id=user_id, message=message, attachment=attachment,
                                      keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))
        else:
            self.vk_api.messages.send(peer_id=user_id, message=message, attachment=attachment,
                                      random_id=randrange(10 ** 7))

    def delete_buttons(self, user_id: int, message: str):
        kb = {"one_time": True, "buttons": []}
        self.vk_api.messages.send(peer_id=user_id, message=message, keyboard=json.dumps(kb),
                                  random_id=randrange(10 ** 7))

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
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.PRIMARY, payload={"type": "stop"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Понравившиеся", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "show_favorites"})
        self.send_msg(user_id, message, None, keyboard)

    def get_age_for_search(self) -> int:
        age = None
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

    def ask_age(self, user_id: int, gender: int) -> tuple:
        """Запрашиваем возраст людей, которых будем искать"""
        ask_message_1 = "Будем искать девушку от:" if gender == 1 else "Будем искать парня от:"
        self.delete_buttons(user_id, ask_message_1)
        age_from = self.get_age_for_search()
        ask_message_2 = "и до:"
        self.send_msg(user_id, ask_message_2)
        age_to = self.get_age_for_search()
        return age_from, age_to

    def ask_gender(self, user_id: int) -> int:
        """Запрашиваем пол людей, которых будем искать"""
        gender = 0
        ask_gender = "Кого будем искать?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label="Девушку", color=VkKeyboardColor.PRIMARY)
        keyboard.add_button(label="Парня", color=VkKeyboardColor.PRIMARY)
        self.send_msg(user_id, ask_gender, None, keyboard)
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_text = event.object.message['text']
                gender = 1 if user_text == "Девушку" else 2
                break
        return gender

    def ask_user_for_search(self, user_info: dict) -> dict:
        """Спрашиваем, верны ли данные для поиска"""
        who = "парня" if user_info["gender"] == 1 else "девушку"
        gender = 2 if user_info["gender"] == 1 else 1

        search_parameters = {"age_from": user_info['age']-1, "age_to": user_info['age'],
                             "gender": gender, "city": user_info['city']['id']}

        message = f"{user_info['first_name']}, будем искать {who} в возрасте {user_info['age']} лет " \
                  f"из г. {user_info['city']['title']}, верно?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "start_search"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "get_new_info_for_search"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Стоп! Я передумал", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "stop"})
        self.send_msg(user_info["user_id"], message, None, keyboard)
        return search_parameters

    def get_new_info_for_search(self, user_id: int) -> dict:
        """Формируем новые параметры для поиска"""
        message = "Хорошо. Задайте параметры для поиска."
        self.delete_buttons(user_id, message)
        gender = self.ask_gender(user_id)
        age_range = self.ask_age(user_id, gender)
        city = self.vk_api.users.get(user_id=user_id, fields="city")
        city_id = city[0]['city']['id']
        search_parameters = {"age_from": age_range[0], "age_to": age_range[1], "gender": gender, "city": city_id}
        return search_parameters

    def buttons_like_dislike(self) -> object:
        """Кнопки LIKE, DISLIKE и STOP для показа результатов поиска пользователю"""
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label="LIKE", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label="DISLIKE", color=VkKeyboardColor.NEGATIVE)
        keyboard.add_line()
        keyboard.add_button(label="Стоп! Хватит!", color=VkKeyboardColor.SECONDARY)
        return keyboard

    def results_over(self, user_id: int):
        """Если все результаты поиска закончились"""
        message = "Увы, но результатов больше нет.\nМожет быть начать новый поиск с другими параметрами?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да, давайте", color=VkKeyboardColor.PRIMARY,
                                     payload={"type": "get_new_info_for_search"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Нет, хватит", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "stop"})
        self.send_msg(user_id, message, None, keyboard)

    def match(self, user_id: int, liked_person_id: int, person_name: str):
        """Проверка на взаимный лайк двух пользователей"""
        match = self.db.check_users_for_match(user_id, liked_person_id)
        if match:
            # сообщение текущему пользователю о взаимном лайке:
            alert_message = "Поздравляем!\nЭтот человек тоже лайкнул вас!"
            alert_photo = "photo-214337223_457239384"
            self.send_msg(user_id, alert_message, alert_photo)
            # сообщение другому пользователю о взаимном лайке:
            result = get_user_info(user_id)
            message_to_another_user = f"{person_name}, вас лайкнули в ответ!\n"\
                                      f"{result['first_name']} {result['last_name']}: https://vk.com/id{user_id}"
            self.send_msg(liked_person_id, message_to_another_user)

    def show_results(self, user_id: int, search_parameters: dict):
        """Показываем каждый результат поиска пользователю"""
        show = True
        for result in search_people(search_parameters):
            if show:
                self.db.check_user_in_founds(result)
                evaluate = self.db.check_like_dislike(user_id, result)
                if evaluate:
                    result_msg = f"{result['first_name']} {result['last_name']}\nпрофиль: {result['profile']}"
                    keyboard = self.buttons_like_dislike()
                    photos = result['photos']
                    self.send_msg(user_id, result_msg, photos, keyboard)
                    for event in self.long_poll.listen():
                        if event.type == VkBotEventType.MESSAGE_NEW:
                            user_text = event.object.message['text']
                            if user_text == "LIKE":
                                self.db.insert_favourite(user_id, result['id'])
                                self.match(user_id, result['id'], result['first_name'])
                                break
                            elif user_text == "DISLIKE":
                                self.db.insert_dislike(user_id, result['id'])
                                break
                            elif user_text == "Стоп! Хватит!":
                                goodbye_msg = "Хорошо, понял.\nХотите еще раз взглянуть на тех, кто вам понравился?"
                                kb = VkKeyboard(one_time=True)
                                kb.add_callback_button(label="Да", color=VkKeyboardColor.SECONDARY,
                                                       payload={"type": "show_favorites"})
                                kb.add_line()
                                kb.add_callback_button(label="Нет", color=VkKeyboardColor.SECONDARY,
                                                       payload={"type": "stop"})
                                self.send_msg(user_id, goodbye_msg, None, kb)
                                show = False
                                break
            else:
                break
        if show:
            self.results_over(user_id)

    def show_favorites(self, user_id: int):
        """Показываем лайкнутых пользователей"""
        favorites = self.db.show_all_favorites(user_id)
        if not favorites:
            message = "Увы, список понравившихся людей пуст.\nМожет быть стоит сначала кого-нибудь найти и посмотреть?"
            self.delete_buttons(user_id, message)
        else:
            message = "Понравившиеся:"
            self.delete_buttons(user_id, message)
            favorites_message = ""
            for person in favorites:
                person_info = f"{person[1]} {person[2]}: {person[3]}\n"
                favorites_message += person_info
            self.send_msg(user_id, favorites_message)
            hope_message = "Неплохо!\nМожет быть кто-нибудь из этих людей тоже однажды лайкнет вас!"
            self.send_msg(user_id, hope_message)

    def start(self):
        """ОСНОВНАЯ ФУНКЦИЯ:
        Отслеживаем события в чате, общаемся с пользователем"""
        search_parameters = {}
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id = event.object.message['from_id']
                user_text = event.object.message['text']
                self.say_hello(user_id, user_text)
                self.start_conversation(user_id)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                user_id = event.object['user_id']
                if event.object.payload.get("type") == "yes_search":
                    user_info = get_user_info(user_id)
                    result = analysis_user_info(user_info)
                    if result:
                        search_parameters = self.ask_user_for_search(user_info)
                    else:
                        error_message = f"У вас не указаны некоторые параметры:\n\n" \
                                        f"Возраст: {user_info['age']}\n" \
                                        f"Город: {user_info['city']}\n" \
                                        f"Пол: {user_info['gender']}\n\n" \
                                        f"Увы, но без полной информации нельзя будет продолжить поиск!\n"\
                                        f"Пожалуйста, обновите свой профиль и возвращайтесь!"
                        self.send_msg(user_id, error_message)
                elif event.object.payload.get("type") == "stop":
                    new_message = "Нет, так нет. До скорой встречи!"
                    self.delete_buttons(user_id, new_message)
                elif event.object.payload.get("type") == "start_search":
                    new_message = "Отлично, погнали!"
                    self.delete_buttons(user_id, new_message)
                    self.show_results(user_id, search_parameters)
                elif event.object.payload.get("type") == "get_new_info_for_search":
                    search_parameters = self.get_new_info_for_search(user_id)
                    self.show_results(user_id, search_parameters)
                elif event.object.payload.get("type") == "show_favorites":
                    self.show_favorites(user_id)
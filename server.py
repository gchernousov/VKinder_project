from random import randrange
from pprint import pprint as pp
import re
import json
import datetime

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class Server:

    def __init__(self, api_token, group_id, server_name: str="Empty"):
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

    def delete_buttons(self, user_id, message):
        kb = {"one_time": True, "buttons": []}
        self.vk_api.messages.send(peer_id=user_id, message=message,
                                  keyboard=json.dumps(kb), random_id=randrange(10 ** 7))

    def analys_event_message_new(self, event) -> tuple:
        """Анализируем сообщение и узнаем id пользователя и текст его сообщения"""
        user_id = event.object.message['from_id']
        text_message = event.object.message['text']
        return user_id, text_message

    def say_hello(self, user_id_and_text: tuple):
        """Ищем приветствие в сообщении. Если оно есть - приветствуем пользователя в ответ"""
        pattern = r"[П/п]ривет|[З|з]дравствуй[\w]*|[H|h]ello|[Х|х]ай|[Д|д]обр[а-я]+ (утро|день|вечер)"
        result = re.findall(pattern, user_id_and_text[1])
        if len(result) != 0:
            user_name = self.vk_api.users.get(user_id=user_id_and_text[0])[0]['first_name']
            msg = f"Привет, {user_name}"
            self.send_msg(user_id_and_text[0], msg)

    def start_conversation(self, user_id):
        msg = "Хотите начать поиск людей для знакомств?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.POSITIVE, payload={"type": "get_info_for_search"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE, payload={"type": "no_search"})
        self.send_msg(user_id, msg, keyboard)

    def start_seacrh_person(self):
        pass

    def get_user_info(self, user_id):
        """Собираем информацию о пользователе"""
        result = self.vk_api.users.get(user_id=user_id, fields="bdate,city,relation,sex")
        if "bdate" in result[0]:
            user_birthday = result[0]["bdate"]
            age = self.get_age(user_birthday)
        else:
            age = None
        if "city" in result[0]:
            city = result[0]["city"]
        else:
            city = None
        user_info = {"user_id": result[0]["id"],
                     "first_name": result[0]["first_name"],
                     "last_name": result[0]["last_name"],
                     "age": age,
                     "city": city,
                     "relation": result[0]["relation"],
                     "gender": result[0]["sex"]}
        return user_info

    def get_age(self, birthday):
        """Узнаем сколько пользователю полных лет"""
        current_date = datetime.date.today()
        now = datetime.date(year=current_date.year, month=current_date.month, day=current_date.day)
        birthday = birthday.split(".")
        bday = datetime.date(year=int(birthday[2]), month=int(birthday[1]), day=int(birthday[0]))
        age = int((now - bday).days / 365)
        return age

    def ask_user_age(self, user_id):
        question = "Сколько вам лет?"
        self.send_msg(user_id, question)

    def ask_user_for_search(self, user_info):
        who = ""
        city = ""
        if user_info["gender"] == 1:
            who = "парня"
        elif user_info["gender"] == 2:
            who = "девушку"
        else:
            pass # уточнить у пользователя пол
        if user_info["age"] is None:
            pass # спросить возраст
            # self.ask_user_age(user_info["user_id"])
        if user_info["city"] is None:
            pass # уточнить город
        else:
            city = user_info["city"]["title"]

        message = f"{user_info['first_name']}, будем искать {who} в возрасте {user_info['age']} лет из г. {city}, верно?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.POSITIVE,
                                     payload={"type": "start_search"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE,
                                     payload={"type": "get_new_info_for_search"})
        keyboard.add_line()
        keyboard.add_callback_button(label="Стоп! Я передумал", color=VkKeyboardColor.SECONDARY,
                                     payload={"type": "stop"})
        self.send_msg(user_info["user_id"], message, keyboard)

    def start(self):
        """ Функция диалога с пользователем"""
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id_and_text = self.analys_event_message_new(event)
                user_id = user_id_and_text[0]
                self.say_hello(user_id_and_text)
                self.start_conversation(user_id)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                user_id = event.object['user_id']
                if event.object.payload.get("type") == "get_info_for_search":
                    user_info = self.get_user_info(user_id)
                    self.ask_user_for_search(user_info)
                    # new_message = "Начинается работа функции start_search_person()"
                    # # self.vk_api.messages.send(peer_id=user_id, message=new_message, random_id=randrange(10 ** 7))
                    # self.send_msg(user_id, new_message)
                elif event.object.payload.get("type") == "no_search":
                    new_message = "Нет, так нет. Как-нибудь в другой раз. До скорой встречи!"
                    self.delete_buttons(user_id, new_message)
                elif event.object.payload.get("type") == "stop":
                    new_message = "Очень жаль. Когда передумаете еще раз, обращайтесь!"
                    self.delete_buttons(user_id, new_message)
                elif event.object.payload.get("type") == "start_search":
                    new_message = "[начинаем поиск людей по заданным параметрам: search_person()]"
                    self.send_msg(user_id, new_message)
                elif event.object.payload.get("type") == "get_new_info_for_search":
                    new_message = "[сбор новых параметров для поиска людей: new_search_options()]"
                    self.send_msg(user_id, new_message)
from random import randrange
from pprint import pprint as pp
import re

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
        self.vk_api.messages.send(peer_id=user_id, message=message,
                                  keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))

    def get_user_name(self, user_id) -> str:
        """Узнаем имя пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def analys_incoming_message(self, event) -> tuple:
        """Анализируем сообщение и узнаем id пользователя и текст его сообщения"""
        user_id = event.object.message['from_id']
        text_message = event.object.message['text']
        return user_id, text_message

    def say_hello(self, user_id_and_text: tuple):
        pattern = r"[П/п]ривет|[З|з]дравствуй[\w]*|[H|h]ello|[Х|х]ай|[Д|д]оброе утро|[Д|д]обрый [день|вечер]+ "
        result = re.findall(pattern, user_id_and_text[1])
        if len(result) != 0:
            user_name = self.get_user_name(user_id_and_text[0])
            msg = f"Привет, {user_name}"
            self.send_msg(user_id_and_text[0], msg)

    def start_conversation(self, user_id):
        msg = "Хотите начать поиск людей для знакомств?"
        keyboard = VkKeyboard(one_time=True)
        keyboard.add_button(label="Да", color=VkKeyboardColor.POSITIVE)
        keyboard.add_button(label="Нет", color=VkKeyboardColor.NEGATIVE)
        self.send_msg(user_id, msg, keyboard)

    def start(self):
        """ Функция диалога с пользователем"""
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id_and_text = self.analys_incoming_message(event)
                user_id = user_id_and_text[0]
                self.say_hello(user_id_and_text)
                self.start_conversation(user_id)
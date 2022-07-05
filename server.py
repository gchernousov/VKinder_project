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
        if keyboard != None:
            self.vk_api.messages.send(peer_id=user_id, message=message,
                                  keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))
        else:
            self.vk_api.messages.send(peer_id=user_id, message=message, random_id=randrange(10 ** 7))

    def get_user_name(self, user_id) -> str:
        """Узнаем имя пользователя"""
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def analys_event_message_new(self, event) -> tuple:
        """Анализируем сообщение и узнаем id пользователя и текст его сообщения"""
        user_id = event.object.message['from_id']
        text_message = event.object.message['text']
        return user_id, text_message

    def analys_event_message_event(self, event):
        user_id = event.object['user_id']
        event_id = event.object['event_id']
        # self.vk_api.messages.sendMessageEventAnswer(event_id=event_id, user_id=user_id,
        #                                             peer_id=user_id, event_data="1111")
        return user_id, event_id

    def say_hello(self, user_id_and_text: tuple):
        pattern = r"[П/п]ривет|[З|з]дравствуй[\w]*|[H|h]ello|[Х|х]ай|[Д|д]обр[а-я]+ (утро|день|вечер)"
        result = re.findall(pattern, user_id_and_text[1])
        if len(result) != 0:
            user_name = self.get_user_name(user_id_and_text[0])
            msg = f"Привет, {user_name}"
            # kb = VkKeyboard(one_time=True)
            self.send_msg(user_id_and_text[0], msg)

    def start_conversation(self, user_id):
        msg = "Хотите начать поиск людей для знакомств?"
        keyboard = VkKeyboard(one_time=True)
        # keyboard.add_button(label="Да", color=VkKeyboardColor.POSITIVE)
        # keyboard.add_button(label="Нет", color=VkKeyboardColor.NEGATIVE)
        # keyboard.add_callback_button(label="КНОПКА 1", payload={'type': 'show_snackbar', 'text': 'Я текст в вспылающем окне'}, color=VkKeyboardColor.PRIMARY)
        # keyboard.add_callback_button(label="КНОПКА 2", payload={'type': 'open_link', 'link': 'https://www.ozon.ru/'}, color=VkKeyboardColor.SECONDARY)
        keyboard.add_callback_button(label="Да", color=VkKeyboardColor.POSITIVE, payload={"type": "press_YES"})
        keyboard.add_callback_button(label="Нет", color=VkKeyboardColor.NEGATIVE, payload={"type": "press_NO"})
        # self.vk_api.messages.sendMessageEventAnswer(peer_id=user_id, message=msg,
        #                           keyboard=keyboard.get_keyboard(), random_id=randrange(10 ** 7))
        self.send_msg(user_id, msg, keyboard)

    def start(self):
        """ Функция диалога с пользователем"""
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                user_id_and_text = self.analys_event_message_new(event)
                user_id = user_id_and_text[0]
                self.say_hello(user_id_and_text)
                self.start_conversation(user_id)
            elif event.type == VkBotEventType.MESSAGE_EVENT:
                user_id_and_event_id = self.analys_event_message_event(event)
                if event.object.payload.get("type") == "press_YES":
                    new_msg = "Начать поиск людей..."
                    self.send_msg(user_id_and_event_id[0], new_msg)
                elif event.object.payload.get("type") == "press_NO":
                    new_msg = "Нет, так нет. Как-нибудь в другой раз. До скорой встречи!"
                    kb = VkKeyboard(one_time=True)
                    kb.add_button(label="EXIT", color=VkKeyboardColor.NEGATIVE)
                    self.send_msg(user_id_and_event_id[0], new_msg, kb)

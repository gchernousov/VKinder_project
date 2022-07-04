from random import randrange
from pprint import pprint as pp

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType


class Server:

    def __init__(self, api_token, group_id, server_name: str="Empty"):
        self.server_name = server_name
        self.vk = vk_api.VkApi(token=api_token)
        self.long_poll = VkBotLongPoll(self.vk, group_id)
        self.vk_api = self.vk.get_api()

    def send_msg(self, send_id, message):
        self.vk_api.messages.send(peer_id=send_id, message=message, random_id=randrange(10 ** 7))

    def start(self):
        for event in self.long_poll.listen():
            if event.type == VkBotEventType.MESSAGE_NEW:
                answer_data = self.get_answer(event)
                if answer_data[1] == "Привет":
                    message = f"Привет, {self.get_user_name(answer_data[0])}!"
                    self.send_msg(answer_data[0], message)

                question = "Хотите найти кого-нибудь для знакомства?"
                self.send_msg(answer_data[0], question)


                # print("Username: " + self.get_user_name(event.object.from_id))
                # print("From: " + self.get_user_city(event.object.from_id))
                # print("Text: " + event.object.text)
                # print("Type: ", end="")
                # if event.object.id > 0:
                #     print("private message")
                # else:
                #     print("group message")
                # print(" --- ")

    def get_user_name(self, user_id):
        return self.vk_api.users.get(user_id=user_id)[0]['first_name']

    def get_user_city(self, user_id):
        return self.vk_api.users.get(user_id=user_id, fields="city")[0]["city"]['title']

    def get_answer(self, event):
        user_id = event.object.message['from_id']
        text_message = event.object.message['text']
        return user_id, text_message

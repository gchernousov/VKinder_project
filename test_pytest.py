import pytest
from parameterized import parameterized

import vk_api
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from server import Server
from config import token, group_id


test_server = Server(token, group_id, "test_server")

# данные для теста:
USER_ID = 716417153 # вставить id своего профиля
kb = VkKeyboard(one_time=True)
kb.add_button(label="test button", color=VkKeyboardColor.PRIMARY)
test_photo = "photo716417153_457239017"

last_name = "Черноусов" # фамилия в профиле vk
birthday = "28.12.1989"
current_age = 32 # кол-во полных лет


class TestServerMethods:

    def setup(self):
        print(">>> setup")

    def teardown(self):
        print(">>> teardown")

    # @parameterized.expand(
    #     [
    #         (USER_ID, "simple message"),
    #         (USER_ID, "message with buttons", kb)
    #     ]
    # )
    # def test_send_msg(self, user_id, msg, kb=None):
    #     # т.к. функция отправки сообщений нам ничего не возвращает, то мы ожидаем None
    #     # если сообщение не будет отправлено, то вместо None будет ошибка
    #     assert test_server.send_msg(user_id, msg, kb) == None
    #
    # def test_send_img(self):
    #     assert test_server.send_img(USER_ID, test_photo) == None

    # def test_get_user_info(self):
    #     user_info = test_server.get_user_info(USER_ID)
    #     assert type(user_info) == dict
    #     assert user_info['last_name'] == last_name

    def test_get_age(self):
        assert test_server.get_age(birthday) == current_age




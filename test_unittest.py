import unittest
from unittest.mock import patch, MagicMock
from parameterized import parameterized

import vk_api
from random import randrange

from server import Server
from config import token, group_id

test_server = Server(token, group_id, "test server")
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()

USER_ID = 716417153

class TestFunctions(unittest.TestCase):

    def setUp(self) -> None:
        print(">>> setUp")

    def tearDown(self) -> None:
        print(">>> tearDown")

    @classmethod
    def setUpClass(cls) -> None:
        print(">>> setUpClass")

    @classmethod
    def tearDownClass(cls) -> None:
        print(">>> tearDownClass")

    # Отправка сообщений через vk_api:
    def test_vk_messages_send(self):
        test_message = "test message"
        response = vk.messages.send(peer_id=USER_ID, message=test_message, random_id=randrange(10 ** 7))
        self.assertIsInstance(response, int)

    # Получение информации о пользователе:
    def test_get_user_info(self):
        expected_result = {"user_id": 716417153, "first_name": "Георгий", "last_name": "Черноусов",
                  "age": 32, "city": {'id': 49, 'title': 'Екатеринбург'}, "gender": 2}
        self.assertEqual(test_server.get_user_info(716417153), expected_result)

    # Вычисление возраста из даты рождения:
    def test_get_age(self):
        birthday = "28.12.1989"
        self.assertEqual(test_server.get_age(birthday), 32)

    # Проверка валидности информации о пользователе:
    @parameterized.expand(
        [
            ({"user_id": 123456789, "first_name": "Имя", "last_name": "Фамилия",
              "age": 30, "city": {'id': 1, 'title': 'Москва'}, "gender": 2}, True),
            ({"user_id": 123456789, "first_name": "Имя", "last_name": "Фамилия",
              "age": 30, "city": "не указан", "gender": 2}, False)
        ]
    )
    @patch("server.Server.send_msg")
    def test_analys_user_info(self, user_info, result, send_msg):
        self.assertEqual(test_server.analys_user_info(user_info), result)

    # Формирование диапазона возраста для поиска:
    @patch("server.Server.send_msg")
    @patch("server.Server.delete_buttons")
    @patch("server.Server.get_age_for_search", side_effect=[26, 28])
    def test_ask_age(self, func, del_btn, send_m):
        expected_result = (26, 28)
        self.assertEqual(test_server.ask_age(USER_ID, 1), expected_result)

    # Формирование параметров для поиска на основе данных пользователя:
    @patch("server.Server.send_msg")
    def test_ask_user_for_search(self, send_msg):
        test_user_info = {"user_id": 123456789, "first_name": "Имя", "last_name": "Фамилия",
                          "age": 30, "city": {'id': 1, 'title': 'Москва'}, "gender": 2}
        expected_search_parameters = {"age_from": 29, "age_to": 31, "gender": 1, "city": 1}
        self.assertEqual(test_server.ask_user_for_search(test_user_info), expected_search_parameters)

    # Формирование новой информации для поиска:
    @patch("server.Server.delete_buttons")
    @patch("server.Server.ask_age", return_value=(26, 29))
    @patch("server.Server.ask_gender", return_value=1)
    def test_get_new_info_for_search(self, get_gender, get_age_range, del_btns):
        self.assertEqual(test_server.get_new_info_for_search(USER_ID), {"age_from": 26, "age_to": 29, "gender": 1, "city": 49})
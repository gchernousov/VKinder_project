import vk_api
from vk_api import VkTools
import datetime
from config import token


class VkBot:
    vk_session = vk_api.VkApi(token=token)
    vk = vk_session.get_api()
    now = datetime.datetime.now()

    def vk_user_search(self, data):
        city = data['city']
        sex = 2 if data['sex'] == 1 else 1
        age = self.now.year - int(data['year'])
        age_from = age - 5 if sex == 1 else age  # Возраст от: на 5 лет младше пользователя, если муж
        age_to = age_from + 5 if sex == 2 else age  # Возраст до: на 5 лет старше пользователя, если жен
        rs = VkTools(self.vk).get_all_iter(
            method='users.search',
            max_count=1000,
            values={'is_closed': False, 'fields': 'relation, bdate', 'hometown': city, 'sex': sex, 'age_from': age_from,
                    'age_to': age_to, 'has_photo': 1, 'status': 6},
            key='items')
        return rs


if __name__ == '__main__':
    b = VkBot()
    #print(b.vk_user_search('35700604'))
    f = b.vk_user_search({'name': 'Игорь', 'sex': 2, 'year': 1997, 'city': 'Екатеринбург'})
    print(f)

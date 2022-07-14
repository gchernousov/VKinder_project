import vk_api
from vk_api import VkTools
import datetime
from pprint import pprint
from my_token import TOKEN  # нужно вставить свой модуль с личным токеном вк
import requests

URL = 'https://vk.com/id'

vk_session = vk_api.VkApi(token=TOKEN)
vk = vk_session.get_api()
now = datetime.datetime.now()


def vk_user_data(id_user):
    """Ф-ия формирует необходимые параметры по пользователю, который ищет половинку."""
    info = vk.users.get(user_ids=id_user, fields='city, bdate, sex')[0]
    year = None if 'bdate' not in info or not info['bdate'][-4:].isnumeric() else info['bdate'][-4:]
    city = None if 'city' not in info else info['city']['title']
    sex = None if 'sex' not in info else info['sex']
    my_info_dict = {'first_name': info['first_name'], 'last_name': info['last_name'], 'sex': sex,
                    'year': year, 'city': city}
    return my_info_dict


# dataa = {'first_name': 'Игорь', 'last_name': 'Грефенштейн', 'sex': 2, 'year': '1997', 'city': 49}   -- тестовый словарь для бота


def vk_users_search(data):  # data = vk_user_data(id профиля вк)
    """Ф-ия по параметрам пользователя из ф-ии vk_user_data подбирает половинку пользователю."""
    city = data['city']
    sex = 2 if data['sex'] == 1 else 1
    age = now.year - int(data['year'])
    age_from = age - 5
    age_to = age + 5
    peoples = VkTools(vk).get_all_iter(  # Модуль для выкачивания множества результатов.
        method='users.search',
        max_count=1000,
        key='items',
        values={'is_closed': False, 'sex': sex, 'city': city, 'age_from': age_from,
                'age_to': age_to, 'has_photo': 1

                }
    )
    return peoples


def get_vk_photos(user_id):
    res = vk_session.method('photos.get', {
        'album_id': 'profile',
        'extended': 1,
        'owner_id': user_id
    })
    info_list_photo = []
    for photo in res['items']:
        likes = photo['likes']['count']
        info_list_photo.append([likes, photo['owner_id'], photo['id'], photo['sizes'][-1]['url']])
    sort_list = sorted(info_list_photo)[-3:]
    return [f"photo{sort_list[0][1]}_{sort_list[0][2]}" for ph in sort_list]


def full_info():
    for person in vk_users_search(dataa):
        photo = get_vk_photos(person['id'])
        vk_link = URL + str(person['id'])
        full_view = {'id': person['id'], 'first_name': person['first_name'], 'last_name': person['last_name'], 'profile': vk_link, 'photos': ','.join(photo)}
        print(full_view)

# vk_users_search(dataa)
# print(get_vk_photos("35700604"))
full_info()

# for person in vk_users_search(dataa):
#   vk_link = URL + str(person['id'])
#  print(person['id'], person['first_name'], person['last_name'], vk_link)

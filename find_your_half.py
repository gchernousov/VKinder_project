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

# dataa = {"age_from": 22, "age_to": 32, "gender": 1, "city": 2}


def vk_users_search(data):  # data = vk_user_data(id профиля вк)
    """Ф-ия по параметрам пользователя из ф-ии vk_user_data подбирает половинку пользователю."""
    city = data['city']
    peoples = VkTools(vk).get_all_iter(  # Модуль для выкачивания множества результатов.
        method='users.search',
        max_count=1000,
        key='items',
        values={'is_closed': False, 'sex': data['gender'], 'city': city, 'age_from': data['age_from'],
                'age_to': data['age_to'], 'has_photo': 1, 'status': 6

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
        if person['is_closed'] == False:
            photo = get_vk_photos(person['id'])
            vk_link = URL + str(person['id'])
            full_view = {'id': person['id'], 'first_name': person['first_name'], 'last_name': person['last_name'],
                     'profile': vk_link, 'photos': ','.join(photo)}
            yield full_view


# vk_users_search(dataa)
# print(get_vk_photos(""))
#full_info()
# for person in vk_users_search(dataa):
#   vk_link = URL + str(person['id'])
#  print(person['id'], person['first_name'], person['last_name'], vk_link)

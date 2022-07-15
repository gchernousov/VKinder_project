import vk_api
from vk_api import VkTools

import configparser

settings = configparser.ConfigParser()
settings.read("settings.ini")
access_token = settings['VK_TOKENS']['access_token']

vk_session = vk_api.VkApi(token=access_token)
vk = vk_session.get_api()


def users_search(search_params, month):
    """Поиск пользователей VK по заданным параметрам"""
    peoples = VkTools(vk).get_all_iter(  # Модуль для выкачивания множества результатов.
        method='users.search',
        max_count=1000,
        key='items',
        values={'sort': 1, 'sex': search_params['gender'], 'city': search_params['city'],
                'age_from': search_params['age_from'], 'age_to': search_params['age_to'],
                'has_photo': 1, 'status': 6, 'birth_month': month}
    )
    return peoples


def get_user_photos(user_id):
    """Поиск трех самых популярных фотографий из профиля пользователя"""
    user_photos = vk.photos.get(album_id="profile", extended=1, owner_id=user_id)
    most_popular_photos = []
    for photo in user_photos['items']:
        likes = photo['likes']['count']
        most_popular_photos.append([likes, photo['id']])
    most_popular_photos = sorted(most_popular_photos)[-3:]
    result = [f"photo{user_id}_{photo[1]}" for photo in most_popular_photos]
    result = ','.join(result)
    return result


def search_people(search_params):
    """Выдача результатов поиска"""
    month = 1
    url = 'https://vk.com/id'
    while month <= 12:
        for person in users_search(search_params, month):
            if person['is_closed'] is False:
                photos = get_user_photos(person['id'])
                vk_link = url + str(person['id'])
                full_info = {'id': person['id'], 'first_name': person['first_name'], 'last_name': person['last_name'],
                             'profile': vk_link, 'photos': photos}
                yield full_info
        month += 1
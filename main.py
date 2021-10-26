from random import randrange
import requests
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id
from datetime import date
import re
from io import BytesIO
from databases.database import *


bot_token = input('Введите токен бота: ')
user_token = input('Введите токен пользователя: ')

vk = vk_api.VkApi(token=bot_token)
longpoll = VkLongPoll(vk)

vk1 = vk.get_api()
upload1 = vk_api.VkUpload(vk1)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7), })


class GetInfoVk:
    url = 'https://api.vk.com/method'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_info(self, user_id):
        acquisition_params = {
            'user_ids': user_id,
            'fields': 'bdate,sex,city,relation'
        }
        response = requests.get(f'{self.url}/users.get', params={**self.params, **acquisition_params}).json()
        return response

    def get_gender(self, user_id):
        gender_value = self.get_info(user_id)['response'][0]['sex']
        if gender_value == 1:
            gender = 'женский'
        elif gender_value == 2:
            gender = 'мужской'
        else:
            gender = self.no_info_gender()
        if gender == 'женский':
            gender_search = 2
        else:
            gender_search = 1
        return gender, gender_search

    def no_info_age(self):
        write_msg(event.user_id, f"Введите свою дату рождения в формате 'ДД.М.ГГ'")
        for event_3 in longpoll.listen():
            if event_3.type == VkEventType.MESSAGE_NEW:
                if event_3.to_me:
                    string = event_3.text
                    re_list = re.search(r'\d{2}\.\d\.\d{4}', string)
                    if re_list is None:
                        write_msg(event_3.user_id, f"Некорректная дата рождения! Введите еще раз")
                    else:
                        return string

    def no_info_gender(self):
        write_msg(event.user_id, f"Введите свой пол")
        for event_4 in longpoll.listen():
            if event_4.type == VkEventType.MESSAGE_NEW:
                if event_4.to_me:
                    if event_4.text in ['мужской', 'Мужской'] or event_4.text in ['женский', 'Женский']:
                        return event_4.text
                    else:
                        write_msg(event_4.user_id, f"Такого пола не бывает...")

    def no_info_city(self):
        write_msg(event.user_id, f"Введите свой город")
        for event_5 in longpoll.listen():
            if event_5.type == VkEventType.MESSAGE_NEW:
                if event_5.to_me:
                    city_search_params = {
                        'country_id': 1,
                        'q': event_5.text,
                    }
                    response = requests.get(f'{self.url}/database.getCities',
                                            params={**self.params, **city_search_params})
                    if len(response.json()['response']['items']) != 0:
                        for r in response.json()['response']['items']:
                            if r['title'] == event_5.text:
                                for r_2 in response.json()['response']['items']:
                                    if r_2 != response.json()['response']['items'][0]:
                                        if r['title'] == r_2['title']:
                                            write_msg(event.user_id, f"Введите свой регион")
                                            for event_5_2 in longpoll.listen():
                                                if event_5_2.type == VkEventType.MESSAGE_NEW:
                                                    if event_5_2.to_me:
                                                        for r_3 in response.json()['response']['items']:
                                                            if r_3['region'] == event_5_2.text:
                                                                return r_3['id'], r_3['title']
                                                            elif r_3 == response.json()['response']['items'][-1]:
                                                                write_msg(event.user_id,
                                                                          f"Такого региона не существует!")
                                        elif r_2 == response.json()['response']['items'][-1]:
                                            for r_4 in response.json()['response']['items']:
                                                if r_4['title'] == event_5.text:
                                                    return r_4['id'], r_4['title']
                            elif r == response.json()['response']['items'][-1]:
                                write_msg(event_5.user_id, f"Такого города не существует! Введите верный город")
                    else:
                        write_msg(event_5.user_id, f"Такого города не существует! Введите верный город")

    def no_info_relation(self, user_id):
        write_msg(event.user_id, f"Введите свое семейное положение")
        for event_6 in longpoll.listen():
            if event_6.type == VkEventType.MESSAGE_NEW:
                if event_6.to_me:
                    status_dict = {'не женат': 1, 'не замужем': 1, 'Не женат': 1, 'Не замужем': 1, 'все сложно': 5,
                                   'Все сложно': 5, 'в активном поиске': 6, 'В активном поиске': 6}
                    if self.get_gender(user_id)[0] in ['мужской', 'Мужской']:
                        if event_6.text in status_dict:
                            return status_dict[event_6.text]
                        else:
                            write_msg(event_6.user_id, f"Такого не бывает...")
                    elif self.get_gender(user_id)[0] in ['женский', 'Женский']:
                        if event_6.text in status_dict:
                            return status_dict[event_6.text]
                        else:
                            write_msg(event_6.user_id, f"Такого не бывает...")

    def age_depend_func(self):
        date_of_birth = self.no_info_age().split('.')
        current_date = str(date.today()).split('-')
        first_date = date(int(date_of_birth[2]), int(date_of_birth[1]), int(date_of_birth[0]))
        second_date = date(int(current_date[0]), int(current_date[1]), int(current_date[2]))
        age = (second_date - first_date).days // 365
        return age

    def get_age(self, user_id):
        if 'bdate' in self.get_info(user_id)['response'][0]:
            string = self.get_info(user_id)['response'][0]['bdate']
            re_list = re.search(r'\d{2}\.\d', string)
            if string == string[re_list.start():re_list.end()]:
                age = self.age_depend_func()
            else:
                date_of_birth = self.get_info(user_id)['response'][0]['bdate'].split('.')
                current_date = str(date.today()).split('-')
                first_date = date(int(date_of_birth[2]), int(date_of_birth[1]), int(date_of_birth[0]))
                second_date = date(int(current_date[0]), int(current_date[1]), int(current_date[2]))
                age = (second_date - first_date).days // 365
        else:
            age = self.age_depend_func()
        return age

    def get_city(self, user_id):
        resp_city = self.get_info(user_id)['response'][0]
        if 'city' in resp_city:
            city_id = resp_city['city']['id']
            city_name = resp_city['city']['title']
        else:
            city = self.no_info_city()
            city_id = city[0]
            city_name = city[1]
        return city_id, city_name

    def get_relation(self, user_id):
        relation = None
        func_call = self.get_info(user_id)['response'][0]
        if 'relation' not in func_call:
            relation = self.no_info_relation(user_id)
        else:
            relation_value = self.get_info(user_id)['response'][0]['relation']
            if relation_value == 1:
                if self.get_gender(user_id) in ['мужской', 'Мужской']:
                    relation = 1
                else:
                    relation = 1
            elif relation_value == 5:
                relation = 5
            elif relation_value == 6:
                relation = 6
            elif relation_value == 0:
                relation = self.no_info_relation(user_id)
        return relation


def info():
    for event_2 in longpoll.listen():
        if event_2.type == VkEventType.MESSAGE_NEW:
            if event_2.to_me:
                obj = GetInfoVk(user_token, '5.131')
                result = obj.get_info(event_2.text)
                if 'error' in result:
                    write_msg(event_2.user_id, f"Такого id или имени пользователя не бывает(")
                else:
                    age = obj.get_age(event_2.text)
                    gender = obj.get_gender(event_2.text)[1]
                    city = obj.get_city(event_2.text)
                    city_id = city[0]
                    city_name = city[1]
                    relation = obj.get_relation(event_2.text)
                    return age, gender, city_id, relation, city_name


def output_depend_func(attach, result2, id_l, event7, photos_dict):
    urls_list = [upload_photo(upload1, j) for j in attach]
    if len(urls_list) == 0:
        iterate = result2['response']['items']
        for el in iterate:
            if el['id'] not in id_l and el['is_closed'] is True:
                continue
            elif el['id'] not in id_l:
                img1 = f'https://vk.com/id{el["id"]}'
                if img1 not in data_list:
                    data_list.append(img1)
                    write_msg(event7.user_id, f'У пользователя нету фото {img1}')
                    id_l.append(el['id'])
                    break
                else:
                    break
    else:
        img2 = f'https://vk.com/id{photos_dict["response"]["items"][0]["owner_id"]}'
        if img2 not in data_list:
            data_list.append(img2)
            write_msg(event7.user_id, img2)
            id_l.append(photos_dict["response"]["items"][0]["owner_id"])
            send_photo(vk1, event.user_id, urls_list)


def new_message(message):
    if message == 'привет' or message == 'Привет':
        write_msg(event.user_id, f"Хай, {event.user_id}")
    elif message == 'найди мне пару' or message == 'Найди мне пару':
        write_msg(event.user_id, f"Введите свой id или имя пользователя")
        obj_2 = UsersSearchVk(user_token, '5.131')
        result_2 = obj_2.users_search(info())
        obj_3 = GetPhotosVk(user_token, '5.131')
        result_3 = obj_3.get_photos(result_2)
        id_list = []
        img = None
        i = 0
        for a, photos in enumerate(result_3):
            top_values = []
            top_photos = {}
            if 'error' in photos:
                if a == 0:
                    i = 1
                continue
            else:
                for photo in photos['response']['items']:
                    count = photo['comments']['count'] + photo['likes']['count']
                    top_photos[count] = photo['id']
                if len(top_photos) > 3:
                    while len(top_values) < 3:
                        top_values.append(top_photos[max(top_photos.keys())])
                        del top_photos[max(top_photos.keys())]
                else:
                    for tp in top_photos:
                        top_values.append(top_photos[tp])
                attachment = []
                for photo in photos['response']['items']:
                    if photo['id'] in top_values:
                        image = photo['sizes'][-3]['url']
                        attachment.append(image)
                if len(photos["response"]["items"]) != 0:
                    img = f'https://vk.com/id{photos["response"]["items"][0]["owner_id"]}'
                else:
                    iterate = result_2['response']['items']
                    for el in iterate:
                        if el['id'] not in id_list and el['is_closed'] is True:
                            continue
                        elif el['id'] not in id_list:
                            img = f'https://vk.com/id{el["id"]}'
                if i == 0 or i == 1:
                    i = 2
                    urls_list = [upload_photo(upload1, j) for j in attachment]
                    if img not in data_list:
                        data_list.append(img)
                        write_msg(event.user_id, img)
                        id_list.append(photos["response"]["items"][0]["owner_id"])
                        send_photo(vk1, event.user_id, urls_list)
                        write_msg(event.user_id, 'Для следующего, введите "далее"')
                    else:
                        continue
                else:
                    if img not in data_list:
                        for event_7 in longpoll.listen():
                            if event_7.type == VkEventType.MESSAGE_NEW:
                                if event_7.to_me:
                                    if event_7.text in ['далее', 'Далее']:
                                        output_depend_func(attachment, result_2, id_list, event_7, photos)
                                        break
                                    else:
                                        write_msg(event_7.user_id, 'Я не понимаю...')
                    else:
                        output_depend_func(attachment, result_2, id_list, event, photos)
        write_msg(event.user_id, 'Больше нету)')
    elif message == 'пока' or message == 'Пока':
        write_msg(event.user_id, "Пока((")
    elif message == 'Начать' or message == 'начать':
        write_msg(event.user_id, 'Введите любое сообщение:\n'
                                 '1. Привет\n'
                                 '2. Найди мне пару\n'
                                 '3. Пока')
    else:
        write_msg(event.user_id, "Не поняла вашего ответа...")


class UsersSearchVk:
    url = 'https://api.vk.com/method'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def users_search(self, func):
        search_params = {
            'count': 1000,
            'city': func[2],
            'age_from': func[0],
            'age_to': func[0],
            'sex': func[1],
            'status': func[3],
            'hometown': func[4],
            'country': 1
        }
        response = requests.get(f'{self.url}/users.search', params={**self.params, **search_params}).json()
        return response


class GetPhotosVk:
    url = 'https://api.vk.com/method/photos.get'

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

    def get_photos(self, users_search_result):
        for i in users_search_result['response']['items']:
            get_photos_params = {
                'owner_id': i['id'],
                'album_id': 'profile',
                'extended': '1'
            }
            response = requests.get(self.url, params={**self.params, **get_photos_params}).json()
            yield response


def upload_photo(vk_upload, photo_url):
    img = requests.get(photo_url).content
    f = BytesIO(img)

    response = vk_upload.photo_messages(f)[0]

    owner_id = response['owner_id']
    photo_id = response['id']
    access_key = response['access_key']
    attachment = f'photo{owner_id}_{photo_id}_{access_key}'

    return attachment


def send_photo(vk2, peer_id, attach):
    vk2.messages.send(
        random_id=get_random_id(),
        peer_id=peer_id,
        attachment=attach
    )


if __name__ == '__main__':
    session = Session()
    session.query(Url).delete()
    session.commit()
    session = Session()
    data_list = []
    cache = []
    num = 0
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                new_message(event.text)
                for dl in data_list:
                    if dl in cache:
                        continue
                    if dl not in cache:
                        cache.append(dl)
                        num += 1
                        url = Url(name=f'url_{num}', url=dl)
                        session.add(url)
                session.commit()

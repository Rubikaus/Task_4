import vk_api
import random
import add
import json
import requests

api_key = ''


def get_button(label, color, payload=""):
    return {
        "action": {
            "type": "text",
            "payload": json.dumps(payload),
            "label": label
        },
        "color": color
    }


keyboard_start = {
    "one_time": False,
    "buttons": [
        [
            get_button(label="Категории", color="default"),
            get_button(label="Новости по категориям", color="default"),
        ],
        [
            get_button(label="Ключевые слова", color="default"),
            get_button(label="Новости по словам", color="default"),
        ]
    ]
}

keyboard_categories = {
    "one_time": False,
    "buttons": [
        [
            get_button(label="Бизнес", color="default"),
            get_button(label="Развлечения", color="default"),
        ],
        [
            get_button(label="Здоровье", color="default"),
            get_button(label="Наука", color="default"),
        ],
        [
            get_button(label="Спорт", color="default"),
            get_button(label="Технологии", color="default"),
        ],
        [
            get_button(label="Главное", color="default"),
            get_button(label="Назад", color="negative"),
        ]
    ]
}

keyboard_keywords = {
    "one_time": False,
    "buttons":
        [
            [
                get_button(label="Добавить слово", color="default"),
                get_button(label="Удалить слово", color="default")
            ],
            [
                get_button(label="Назад", color="negative")
            ]
        ]
}

keyboard_categories = json.dumps(keyboard_categories, ensure_ascii=False).encode("utf-8")
keyboard_categories = str(keyboard_categories.decode("utf-8"))
keyboard_start = json.dumps(keyboard_start, ensure_ascii=False).encode("utf-8")
keyboard_start = str(keyboard_start.decode("utf-8"))
keyboard_keywords = json.dumps(keyboard_keywords, ensure_ascii=False).encode("utf-8")
keyboard_keywords = str(keyboard_keywords.decode("utf-8"))

add.create_database()
vk = vk_api.VkApi(token=api_key)
vk._auth_token()

words = {
    "бизнес": "business",
    "развлечения": "entertainment",
    "здоровье": "health",
    "наука": "science",
    "спорт": "sports",
    "технологии": "technology",
    "главное": "general"
}
categories = ["business", "entertainment", "health", "science", "sports", "technology", "general"]
flag = False
flag_del = False
while True:
    messages = vk.method("messages.getConversations", {"offset": 0, "count": 20, "filter": "unread"})
    if messages["count"] > 0:
        msg = messages['items'][0]['last_message']['text'].lower()
        conversation_id = messages['items'][0]['last_message']['conversation_message_id']
        user_id = messages['items'][0]['last_message']['from_id']
        first_name = vk.method('users.get', {'user_ids': user_id})[0]['first_name']
        last_name = vk.method('users.get', {'user_ids': user_id})[0]['last_name']
        if flag is True:
            add.add_keywords(user_id, msg)
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Слово добавлено",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            flag = False
        elif flag_del is True:
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Слово удалено",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            add.del_keywords(user_id, msg)
            flag_del = False
        elif msg in words:
            vk.method("messages.send",
                      {"peer_id": user_id, "message": add.edit_categ(user_id, words[msg], msg),
                       'random_id': random.randint(1, 231456735)})
        elif add.user_exist(user_id) is None and msg == "привет":
            add.reg_user(user_id, first_name, last_name)
            vk.method("messages.send",
                      {"peer_id": user_id, "message": f"{first_name}, Вы были зарегистрированы",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
        elif add.user_exist(user_id) is not None and msg == "привет":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Вы уже зарегистрированы",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})

        elif msg == "категории":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Выберите понравишуюся категорию",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_categories})
        elif msg == "назад":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Вы попали в главное меню",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
        elif msg == "новости по категориям":
            ex_cat = add.select_req(user_id)
            for i in range(1, 8):
                if ex_cat[i] == 1:
                    link = f"https://newsapi.org/v2/top-headlines?apiKey=2df071e0ab3c417d9626cef194e3d41a&country=ru&category={categories[i - 1]}&pageSize=3"
                    link = requests.get(link)
                    link = link.json()
                    total_result = link['totalResults']
                    if total_result > 3:
                        total_result = 3
                    vk.method("messages.send",
                              {"peer_id": user_id, "message": categories[i - 1].capitalize(),
                               'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
                    for n in range(0, total_result):
                        string = str(link['articles'][n]['title']) + '\n' + str(link['articles'][n]['url'])
                        vk.method("messages.send",
                                  {"peer_id": user_id, "message": string,
                                   'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
        elif msg == "ключевые слова":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Нажмите добавить или удалить и введите ключевое слово",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
        elif msg == "добавить слово":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Введите слово которое хотите добавить",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            flag = True
        elif msg == "удалить слово":
            vk.method("messages.send",
                      {"peer_id": user_id, "message": "Введите слово которое хотите удалить",
                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_keywords})
            flag_del = True
        elif msg == "новости по словам":
            if len(add.select_keywords(user_id)[0]) > 0:
                for word in add.select_keywords(user_id):
                        link = f"https://newsapi.org/v2/top-headlines?sortBy=publishedAt&apiKey=2df071e0ab3c417d9626cef194e3d41a&q={word}&pageSize=3"
                        link = requests.get(link)
                        link = link.json()
                        total_result = link['totalResults']
                        if total_result > 3:
                            total_result = 3
                        elif total_result == 0:
                            vk.method("messages.send",
                                      {"peer_id": user_id, "message": str(word.capitalize() + "\nНовостей по данному слову не найденно"),
                                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
                            continue
                        vk.method("messages.send",
                                  {"peer_id": user_id, "message": word.capitalize(),
                                   'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
                        for n in range(0, total_result):
                            string = str(link['articles'][n]['title']) + '\n' + str(link['articles'][n]['url'])
                            vk.method("messages.send",
                                      {"peer_id": user_id, "message": string,
                                       'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})
            else:
                vk.method("messages.send",
                          {"peer_id": user_id, "message": "У Вас нет активных подписок",
                           'random_id': random.randint(1, 231456735), "keyboard": keyboard_start})



        vk.method("messages.markAsRead", {"peer_id": user_id})

# -*- coding: utf-8 -*-

CITIES = ['Москва', 'Лондон', 'Вена', 'Тбилиси', 'Нижний Новгород']

FLIGHT_SCHEDULE = {
    'Москва': {'Лондон': [{'day': 'Пн/', 'tm_hour': 12, 'tm_min': 00},
                          {'day': 'Ср/', 'tm_hour': 13, 'tm_min': 10}],
               'Вена': [{'tm_year': 2021, 'tm_mon': 5, 'tm_mday': 15, 'tm_hour': 18, 'tm_min': 5}],
               'Тбилиси': [{'tm_year': 2021, 'tm_mon': 9, 'tm_mday': 23, 'tm_hour': 3, 'tm_min': 30}],
               'Нижний Новгород': [
                   {'tm_year': 2021, 'tm_mon': 8, 'tm_mday': 23, 'tm_hour': 12, 'tm_min': 50}]},
    'Лондон': {'Москва': [{'tm_mday': 10, 'tm_hour': 5, 'tm_min': 40},
                          {'tm_mday': 20, 'tm_hour': 7, 'tm_min': 30}],
               'Вена': [{'tm_year': 2021, 'tm_mon': 7, 'tm_mday': 29, 'tm_hour': 9, 'tm_min': 30}],
               'Тбилиси': [{'tm_year': 2021, 'tm_mon': 7, 'tm_mday': 6, 'tm_hour': 8, 'tm_min': 20}],
               'Нижний Новгород': [
                   {'tm_year': 2021, 'tm_mon': 10, 'tm_mday': 3, 'tm_hour': 4, 'tm_min': 00}]},
    'Вена': {'Москва': [{'tm_year': 2021, 'tm_mon': 11, 'tm_mday': 25, 'tm_hour': 21, 'tm_min': 10}],
             'Лондон': [{'tm_year': 2021, 'tm_mon': 10, 'tm_mday': 11, 'tm_hour': 22, 'tm_min': 30}],
             'Тбилиси': [{'tm_year': 2021, 'tm_mon': 9, 'tm_mday': 22, 'tm_hour': 10, 'tm_min': 30}],
             'Нижний Новгород': [
                 {'tm_year': 2021, 'tm_mon': 8, 'tm_mday': 23, 'tm_hour': 12, 'tm_min': 50}]},
    'Тбилиси': {'Москва': [{'tm_year': 2021, 'tm_mon': 10, 'tm_mday': 3, 'tm_hour': 18, 'tm_min': 25}],
                'Лондон': [{'tm_year': 2021, 'tm_mon': 9, 'tm_mday': 12, 'tm_hour': 23, 'tm_min': 00}],
                'Вена': [{'tm_year': 2021, 'tm_mon': 12, 'tm_mday': 28, 'tm_hour': 1, 'tm_min': 30}],
                'Нижний Новгород': [{'tm_year': 2021, 'tm_mon': 10, 'tm_mday': 23, 'tm_hour': 12, 'tm_min': 50}]},
    'Нижний Новгород': {'Москва': [{'tm_year': 2021, 'tm_mon': 6, 'tm_mday': 2, 'tm_hour': 11, 'tm_min': 55}],
                        'Лондон': [{'tm_year': 2021, 'tm_mon': 11, 'tm_mday': 18, 'tm_hour': 15, 'tm_min': 00}],
                        'Вена': [{'tm_year': 2021, 'tm_mon': 12, 'tm_mday': 14, 'tm_hour': 20, 'tm_min': 30}],
                        'Тбилиси': [{'tm_year': 2021, 'tm_mon': 9, 'tm_mday': 29, 'tm_hour': 7, 'tm_min': 30}]}
}

HELP_ANSWER = 'Я могу искать и бронировать билеты. Для старта бронирования билетов напишите "/ticket". ' \
              'Для вызова справки напишите "/help"'


INTENTS = [
    {
        'name': 'Справка',
        'tokens': ('/help', 'помоги', 'умеешь', 'возмжности', 'работаешь'),
        'scenario': None,
        'answer': HELP_ANSWER
    },
    {
        'name': 'Бронирование',
        'tokens': ('/ticket', 'заказать', 'бронировать', 'оформить', 'поиск', 'билет'),
        'scenario': 'ticket_order',
        'answer': None
    },
    {
        'name': 'Приветствие',
        'tokens': ('привет', 'здравствуй', 'ку', 'hi', 'hello', 'приветствую', 'хай', '/ticket'),
        'scenario': 'ticket_order',
        'answer': None
    }
]

SCENARIO = {
    'ticket_order': {
        'first_step': 'step1',
        'steps': {
            'step1': {
                'text': 'Для начала заказа введите город отправления из списка: \n'
                        'Москва,\nЛондон,\nВена,\nТбилиси,\nНижний Новгород',
                'failure_text': 'Введите доступный город',
                'handler': 'handler_departure_city',
                'next_step': 'step2'
            },
            'step2': {
                'text': 'Введите город прибтия из списка: \n'
                        'Москва,\nЛондон,\nВена,\nТбилиси,\nНижний Новгород',
                'failure_text': 'Введите доступный город',
                'handler': 'handler_destination_city',
                'next_step': 'step3'
            },
            'step3': {
                'text': 'Введите дату отправления ввиде "ДД.ММ.ГГГГ"',
                'failure_text': 'Неверный ввод. Введите дату еще раз',
                'handler': 'handler_dates',
                'next_step': 'step4'
            },
            'step4': {
                'text': 'Выбор рейса\n'
                        '{departure_city} - {destination_city}\n'
                        '{date_of_flight}\n'
                        'Выберите номер рейса',
                'failure_text': 'Неверный ввод или рейсов нету.\n'
                                'Введите /ticket что бы повторить запрос',
                'handler': 'handler_flight',
                'next_step': 'step5'
            },
            'step5': {
                'text': 'Укажите колличество пассажиров (от 1 до 5)',
                'failure_text': 'Неверный ввод. Введите число от 1 до 5',
                'handler': 'handler_passengers',
                'next_step': 'step6'
            },
            'step6': {
                'text': 'Введите комментарий',
                'failure_text': '',
                'handler': 'handler_comment',
                'next_step': 'step7'
            },
            'step7': {
                'text': 'Проверьте введенные данные:\n'
                        'Город отправления - {departure_city}\n'
                        'Город назначения - {destination_city}\n'
                        'Номер рейса - {flight}\n'
                        'Число пасссажиров - {quantity_passengers}\n'
                        'Коментарий - {comment}\n'
                        'Все данные верны? (да/нет)',
                'failure_text': 'Положительного ответа не поступило, повторить запрос?',
                'handler': 'handler_answer',
                'next_step': 'step8'
            },
            'step8': {
                'text': 'Введите номер телефона для связи в формате +7ХХХХХХХХХХ',
                'failure_text': 'Неверный ввод. Введите номер в требуемом формате',
                'image': 'generate_ticket_handler',
                'handler': 'handler_phone_number',
                'next_step': 'step9'
            },
            'step9': {
                'text': 'Заявка создана, с вами свяжутся по указанному телефону для подтверждения заказа',
                'failure_text': None,
                'handler': None,
                'next_step': None
            }
        }

    }
}

DB_CONFIG = dict(
    provider='postgres',
    user='postgres',
    password='lifor131994',
    host='localhost',
    database='vk_chat_bot',
    port='5432'
)

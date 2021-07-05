# -*- coding: utf-8 -*-
from datetime import datetime
import re
from generate_ticket import generate_ticket

re_name = re.compile(r'^[\w\-\s]{3, 40}$')

re_moscow = re.compile(r'[Мм]оскв[\w]{,2}')
re_london = re.compile(r'[Лл]ондо[\w]{,2}')
re_vena = re.compile(r'[Вв]ен[\w]{,2}')
re_tbilisi = re.compile(r'[Тт]били[\w]{,3}')
re_nn = re.compile(r'[Нн]иж[\w]{,3}|[Нн]овго[\w]{,3}')
re_phone_nmber = re.compile(r'\+7[\d]{10}')

cities = {
    re_moscow: 'Москва',
    re_london: 'Лондон',
    re_vena: 'Вена',
    re_tbilisi: 'Тбилиси',
    re_nn: 'Нижний Новгород'
}


def handler_departure_city(text: str, context):
    for elem in cities:
        town = elem.match(text)
        if town:
            city = cities[elem]
            context['departure_city'] = city
            return city
    return False


def handler_destination_city(text: str, context):
    for elem in cities:
        town = elem.match(text)
        if town:
            city = cities[elem]
            context['destination_city'] = city
            return city
    return False


def handler_dates(text, context):
    try:
        dates = datetime.strptime(text, '%d.%m.%Y')
    except ValueError:
        return False
    else:
        timedelta = (dates - datetime.now()).days
        if timedelta >= 0:
            context['date'] = str(dates.date())
            return dates.date()
        return False


def handler_flight(text, context):
    if 0 < int(text) < 6:
        context['flight'] = f'рейс №{int(text)}'
        return int(text)
    else:
        return False


def handler_passengers(text, context):
    if 0 < int(text) < 6:
        context['quantity_passengers'] = int(text)
        return int(text)
    else:
        return False


def handler_comment(text, context):
    context['comment'] = text
    return text


def handler_answer(text, context: None):
    if text.lower() == 'да':
        return True
    else:
        return False


def handler_phone_number(text, context):
    phone_number = text
    if re_phone_nmber.match(phone_number):
        context['phone_num'] = phone_number
        return True
    else:
        return False


def generate_ticket_handler(text, context):
    departure = context['departure_city']
    destination = context['destination_city']
    date = context['date_of_flight']
    passengers = context['quantity_passengers']
    return generate_ticket(departure, destination, date, passengers)

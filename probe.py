import datetime

import handlers
from models import UserState, Registration

try:
    import settings
    import settings_for_bot
except ImportError:
    exit('Do cp settings.py.default settings.py and set token')

import logging
import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
from pony.orm import db_session

group_id = 202285296

log = logging.getLogger('bot')


def configure_logging():
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter('%(levelname)s %(message)s'))
    stream_handler.setLevel(logging.INFO)
    log.addHandler(stream_handler)

    file_handler = logging.FileHandler('bot.log.txt')
    file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s', datefmt='%d-%m-%Y %H-%M'))
    file_handler.setLevel(logging.DEBUG)
    log.addHandler(file_handler)
    log.setLevel(logging.DEBUG)


class Bot:
    """
    Echo bot for vk.com
    Use python 3.8:
    """

    def __init__(self, group_id, token):
        """
        :param group_id: group id from vk group
        :param token: secret token
        """
        self.group_id = group_id
        self.token = token

        self.vk = vk_api.VkApi(token=token)
        self.long_poller = VkBotLongPoll(self.vk, self.group_id)

        self.api = self.vk.get_api()

    def run(self):
        """run bot"""
        for event in self.long_poller.listen():
            try:
                self.on_event(event)
            except Exception:
                log.exception('ошибка в обработке события')

    @db_session
    def on_event(self, event):
        """
        Send message back if it is text

        :param event: VkBotMessageEvent object
        :return: None
        """
        if event.type != VkBotEventType.MESSAGE_NEW:
            log.info('Мы пока не умеем обрабатывать событие такого типа %s', event.type)
            return

        user_id = event.object.peer_id
        text = event.object.text
        state = UserState.get(user_id=str(user_id))

        if state is not None:
            text_to_send = self.continue_scenario(user_id, text, state)
        else:
            # search intent
            for intent in settings_for_bot.INTENTS:
                log.debug(f'User gets {intent}')
                if any(token in text.lower() for token in intent['tokens']):
                    if intent['answer']:
                        text_to_send = intent['answer']
                    else:
                        text_to_send = self.start_scenario(intent['scenario'], user_id)
                    break
            else:
                text_to_send = settings_for_bot.HELP_ANSWER

        self.send_message(text_to_send, user_id)

    @staticmethod
    def start_scenario(scenario_name, user_id):
        scenario = settings_for_bot.SCENARIO[scenario_name]
        first_step = scenario['first_step']
        step = scenario['steps'][first_step]
        text_to_send = step['text']
        UserState(user_id=str(user_id), scenario_name=scenario_name, step_name=first_step, context={})
        return text_to_send

    def continue_scenario(self, user_id, text, state):
        if text in ['/help', '/ticket']:
            if text == '/ticket':
                state.delete()
                text_to_send = 'Запрос будет повторен, введите запрос:\n' \
                               '/ticket - начать заказ билетов\n' \
                               '/help - вывести справку'
                return text_to_send
            for intent in settings_for_bot.INTENTS:
                if intent['answer']:
                    self.send_message(text_to_send=intent['answer'], user_id=str(user_id))
                else:
                    self.start_scenario(intent, user_id)
            state.delete()

        steps = settings_for_bot.SCENARIO[state.scenario_name]['steps']
        step = steps[state.step_name]
        handler = getattr(handlers, step['handler'])
        message = handler(text=text, context=state.context)

        if message:
            # next step
            next_step = steps[step['next_step']]
            if next_step['next_step']:
                state.step_name = step['next_step']
                if state.step_name == 'step4':
                    self.date_flight(state)
                    if len(self.schedule) == 0:
                        state.delete()
                        text_to_send = next_step['failure_text']
                        return text_to_send
            else:
                #  finish scenario
                log.info(state.context)
                Registration(
                    departure_cities=state.context['departure_city'],
                    destination_cities=state.context['destination_city'],
                    dates=state.context['date_of_flight'],
                    flights=state.context['flight'],
                    quantity_passengers=str(state.context['quantity_passengers']),
                    comments=state.context['comment'],
                    phone_numbers=state.context['phone_num']
                )
                state.delete()

            text_to_send = next_step['text'].format(**state.context)

        else:
            # retry current step
            text_to_send = step['failure_text']

        return text_to_send

    def date_flight(self, state):
        self.schedule = []
        flight_date = str(state.context['date']).split('-')
        year = int(flight_date[0])
        month = int(flight_date[1])
        day = int(flight_date[2])
        timetable = settings_for_bot.FLIGHT_SCHEDULE[state.context['departure_city']][state.context['destination_city']]
        if len(timetable[0]) == 5:
            self.exact_day(timetable, year, month, day, state)
        if 'day' in timetable[0]:
            self.flights_by_days_of_week(timetable, year, month, state)
        if 'tm_year' in timetable[0] and len(timetable[0]) != 5:
            self.flights_by_dates(timetable, state)

    def exact_day(self, timetable, year, month, day, state):
        dates = datetime.datetime.strptime(state.context['date'], '%Y-%m-%d')
        present = datetime.datetime.now()
        answer = datetime.datetime(timetable[0]['tm_year'], timetable[0]['tm_mon'], timetable[0]['tm_mday'],
                                   timetable[0]['tm_hour'], timetable[0]['tm_min'])
        timedelta = (dates - present).days
        state.context['date_of_flight'] = " ".join(self.schedule)
        if timedelta > 0:
            if timetable[0]['tm_year'] >= year:
                if int(present.month) <= month <= timetable[0]['tm_mon']:
                    if month == int(present.month) and int(present.day) <= day <= timetable[0]['tm_mday']:
                        self.schedule.append(answer.strftime('%Y.%m.%d %H:%M'))
                    elif month > int(present.month):
                        self.schedule.append(answer.strftime('%Y.%m.%d %H:%M'))
                state.context['date_of_flight'] = " ".join(self.schedule)

    def flights_by_days_of_week(self, timetable, year, month, state):
        present = datetime.datetime.now()
        for i in range(len(timetable)):
            if present.year <= year:
                if present.month <= month:
                    hour_and_minutes = datetime.time(hour=int(timetable[i]["tm_hour"]),
                                                     minute=int(timetable[i]["tm_min"]))
                    self.schedule.append(
                        f'№{i + 1} {timetable[i]["day"]} - {hour_and_minutes}\n')
        state.context['date_of_flight'] = " ".join(self.schedule)

    def flights_by_dates(self, timetable, state):
        schedule_by_date = []
        early_flight = []
        present = datetime.datetime.now()
        date = datetime.datetime.strptime(state.context['date'], '%Y-%m-%d')
        for i in range(len(timetable)):
            if present <= date:
                time_schedule = datetime.datetime(year=present.year, month=present.month,
                                                  day=timetable[i]["tm_mday"],
                                                  hour=int(timetable[i]["tm_hour"]),
                                                  minute=int(timetable[i]["tm_min"]))
                schedule_by_date.append(time_schedule)
        for elem in schedule_by_date:
            timedelta = (elem - present)
            early_flight.append(timedelta)

        early_flight_index = early_flight.index(min(early_flight))
        answer = schedule_by_date[early_flight_index]
        self.schedule.append(f'№1 {answer}')
        state.context['date_of_flight'] = " ".join(self.schedule)

    def send_message(self, text_to_send, user_id):
        self.api.messages.send(
            message=text_to_send,
            random_id=get_random_id(),
            peer_id=user_id
        )


if __name__ == '__main__':
    configure_logging()
    bot = Bot(settings.GROUP_ID, settings.TOKEN)
    bot.run()

# -*- coding: utf-8 -*-

from copy import deepcopy
from unittest import TestCase
from unittest.mock import patch, Mock

from pony.orm import db_session, rollback
from vk_api.bot_longpoll import VkBotMessageEvent

from chatbot import Bot
import settings_for_bot

from generate_ticket import generate_ticket


def isolate_db(test_func):
    def wrapper(*args, **kwargs):
        with db_session:
            test_func(*args, **kwargs)
            rollback()
    return wrapper


class Test1(TestCase):
    RAW_EVENT = {
        'type': 'message_new',
        'object': {'date': 1619203786, 'from_id': 227194126, 'id': 71, 'out': 0, 'peer_id': 227194126,
                   'text': 'хехе', 'conversation_message_id': 70, 'fwd_messages': [], 'important': False,
                   'random_id': 0, 'attachments': [], 'is_hidden': False},
        'group_id': 202285296}

    def test_run(self):
        count = 5
        obj = [{'a': 1}]
        event = [obj] * count
        long_poller_mock = Mock(return_value=event)
        long_poller_listen_mock = Mock()
        long_poller_listen_mock.listen = long_poller_mock

        with patch('chatbot.vk_api.VkApi'):
            with patch('chatbot.VkBotLongPoll', return_value=long_poller_listen_mock):
                bot = Bot('', '')
                bot.on_event = Mock()
                bot.send_image = Mock()
                bot.run()

                bot.on_event.assert_called()
                bot.on_event.assert_any_call(obj)
                self.assertEqual(bot.on_event.call_count, count)

    INPUTS = ['Что ты умеешь', '/ticket', 'Москва', 'Питер', 'Тбилиси', '23.09.2021',
              '1', '2', 'Место у окна', 'Да', '+79159539780']

    EXECUTED_OUTPUTS = [
        settings_for_bot.HELP_ANSWER,
        settings_for_bot.SCENARIO['ticket_order']['steps']['step1']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step2']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step2']['failure_text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step3']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step4']['text'].format(departure_city='Москва',
                                                                                   destination_city='Тбилиси',
                                                                                   date_of_flight='2021.09.23 03:30'),
        settings_for_bot.SCENARIO['ticket_order']['steps']['step5']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step6']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step7']['text'].format(departure_city='Москва',
                                                                                   destination_city='Тбилиси',
                                                                                   flight='рейс №1',
                                                                                   quantity_passengers='2',
                                                                                   comment='Место у окна'),
        settings_for_bot.SCENARIO['ticket_order']['steps']['step8']['text'],
        settings_for_bot.SCENARIO['ticket_order']['steps']['step9']['text'],
    ]

    @isolate_db
    def test_run_ok(self):
        send_mock = Mock()
        api_mock = Mock()
        api_mock.messages.send = send_mock

        events = []
        for input_text in self.INPUTS:
            event = deepcopy(self.RAW_EVENT)
            event['object']['text'] = input_text
            events.append(VkBotMessageEvent(event))

        long_pooller_mock = Mock()
        long_pooller_mock.listen = Mock(return_value=events)

        with patch('chatbot.VkBotLongPoll', return_value=long_pooller_mock):
            bot = Bot('', '')
            bot.api = api_mock
            bot.send_image = Mock()
            bot.run()

        assert send_mock.call_count == len(self.INPUTS)

        real_outputs = []
        for call in send_mock.call_args_list:
            args, kwargs = call
            real_outputs.append(kwargs['message'])
        assert real_outputs == self.EXECUTED_OUTPUTS

    def test_image_generation(self):
        ticket_file = generate_ticket('Москва', 'Лондон', '20.10.2021', '2', '2')
        with open('test/ticket_example.png', 'rb') as expected_file:
            expected_bytes = expected_file.read()
        assert ticket_file.read() == expected_bytes

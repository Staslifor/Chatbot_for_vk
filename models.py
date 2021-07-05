# -*- coding: utf-8 -*-

from pony.orm import Database, Required, Json

from settings_for_bot import DB_CONFIG

db = Database()
db.bind(**DB_CONFIG)


class UserState(db.Entity):
    """Состоние пользователя внутри сценария"""

    user_id = Required(str, unique=True)
    scenario_name = Required(str)
    step_name = Required(str)
    context = Required(Json)


class Registration(db.Entity):
    """Заявка на регистрацию"""

    departure_cities = Required(str)
    destination_cities = Required(str)
    dates = Required(str)
    flights = Required(str)
    quantity_passengers = Required(str)
    comments = Required(str)
    phone_numbers = Required(str)


db.generate_mapping(create_tables=True)

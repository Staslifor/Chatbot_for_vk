# --*-- coding: utf-8 -*-

from io import BytesIO
import random
from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = 'ticket/avia_ticket.png'
FONT_PATH = 'ticket/Roboto-Regular.ttf'
FONT_SIZE = 40
BLACK = (0, 0, 0, 255)
DEP_OF_SET = (350, 120)
DEST_OF_SET = (300, 212)
DATE_OF_SET = (310, 305)
PASSENG_OF_SET = (620, 397)
AVATAR_SET = (870, 112)


def generate_ticket(departure, destination, date, passengers, ava=None):
    if ava is None:
        rand = random.randint(1, 2)
        avatar = Image.open(f'ticket\\avatar_{str(rand)}.png').convert('RGBA')
    else:
        avatar = Image.open(f'ticket\\avatar_{ava}.png').convert('RGBA')
    base = Image.open(TEMPLATE_PATH).convert('RGBA')
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)

    draw = ImageDraw.Draw(base)
    draw.text(DEP_OF_SET, departure, font=font, fill=BLACK)
    draw.text(DEST_OF_SET, destination, font=font, fill=BLACK)
    draw.text(DATE_OF_SET, date, font=font, fill=BLACK)
    draw.text(PASSENG_OF_SET, str(passengers), font=font, fill=BLACK)

    draw.text((1215, 180), departure, font=font, fill=BLACK)
    draw.text((1170, 260), destination, font=font, fill=BLACK)
    draw.text((1180, 340), date, font=font, fill=BLACK)
    draw.text((1355, 420), str(passengers), font=font, fill=BLACK)

    base.paste(avatar, AVATAR_SET)

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file

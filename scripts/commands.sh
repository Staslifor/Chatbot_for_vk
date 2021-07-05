#!/usr/bin/env bash

# ������ ������ � �������
python -m unittest

# coverage
coverage run --source=bot,handlers,settings -m unittest
coverage report -m

# creat PostgreSQL database
psql -c "create database vk_chat_bot"
psql -d vk_chat_bot

import datetime
import logging

import telegram

import tbs.settings
import tbs.docparse
from croniter import croniter
from typing import Dict, List, Tuple, Iterable

cron_items = {}  # type: Dict[str, croniter]
next_executions =[]  # type: List[Tuple[str, datetime.datetime]]


def set_schedules(start_time=None):
    global cron_items, next_executions
    if start_time is None:
        start_time = datetime.datetime.now()
    commands = tbs.docparse.commands
    cron_items = {
        filename: croniter(
            commands[filename]['schedule'],
            start_time=start_time,
            ret_type=datetime.datetime)
        for filename in commands if commands[filename]['schedule'] is not None
    }
    next_executions = sorted((schedule[0], schedule[1].get_next()) for schedule in cron_items.items())


def execute(filename: str, bot: telegram.bot.Bot) -> Iterable[Dict]:
    logging.info(f'Starting schedule for: {filename}')
    chat = telegram.Chat(-1, 'private')
    message = telegram.Message(-1, {'first_name': 'robot', 'last_name': None}, datetime.datetime.now(), chat)
    update = telegram.Update(-1, message=message)
    result = tbs.docparse.run_command(bot, update, f"{bot.first_name} {filename.split('.')[0]}", -1)
    return result


def process_schedule_now(bot: telegram.bot) -> Iterable[Iterable[Dict]]:
    for tup in next_executions[:]:
        if tup[1] <= datetime.datetime.now():
            yield execute(tup[0], bot)
            next_executions.remove(tup)
            next_executions.append((tup[0], cron_items[tup[0]].get_next()))

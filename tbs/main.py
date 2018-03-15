import logging

import tbs.strings
from tbs import user_callbacks
from . import telegram_callbacks
from . import settings
from .settings import TOKEN
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater, Job

from tbs.docparse import subscribe_commands
from tbs.scheduler import set_schedules


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=settings.LOGLEVEL)
    tbs.strings.setup_strings()

    user_callbacks.setup_callbacks()
    subscribe_commands()
    set_schedules()
    message_handler = MessageHandler(Filters.text,
                                     telegram_callbacks.message_callback)
    dispatcher.add_handler(message_handler)
    logging.info('Starting')
    updater.start_polling(clean=True)
    logging.info('Set message log')
    j = updater.job_queue
    j.put(Job(telegram_callbacks.timed_message, 5.0, repeat=True))
    j.put(Job(telegram_callbacks.process_schedule, 60.0, repeat=True))
    updater.bot.send_message(settings.DEFAULT_CHANNEL, tbs.strings.STARTUP_MESSAGE)

    updater.idle()


if __name__ == '__main__':
    main()

import logging

import tbs.strings
from tbs import user_callbacks
from . import telegram_callbacks
from . import settings
from .settings import TOKEN
from telegram.ext import MessageHandler, Filters
from telegram.ext import Updater

from tbs.docparse import subscribe_commands
from tbs.scheduler import set_schedules


def main():
    updater = Updater(token=TOKEN)
    dispatcher = updater.dispatcher
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=settings.LOGLEVEL)
    tbs.strings._setup_strings()

    user_callbacks._setup_callbacks()
    subscribe_commands()
    set_schedules()
    message_handler = MessageHandler(Filters.text,
                                     telegram_callbacks.message_callback)
    dispatcher.add_handler(message_handler)
    logging.info('Starting')
    updater.start_polling(clean=True)
    logging.info('Set message log')
    j = updater.job_queue
    j.run_repeating(callback=telegram_callbacks.timed_message, interval=5)
    j.run_repeating(callback=telegram_callbacks.process_schedule, interval=60)
    updater.bot.send_message(
        settings.DEFAULT_CHANNEL,
        tbs.strings.STARTUP_MESSAGE)

    updater.idle()


if __name__ == '__main__':
    main()

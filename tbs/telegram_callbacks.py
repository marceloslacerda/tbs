import base64
import datetime
import inspect
import logging
from functools import wraps
from io import BytesIO
from typing import Callable, Dict, Any, Iterable, List

import binascii

from . import settings
import telegram
from . import text_util
from . import docparse
from .acl import isbotmetioned, isprivatemessage
from tbs import user_callbacks
from . import scheduler
from telegram import TelegramError
from telegram.ext import Job


TelegramCallbackReturn = Iterable[Dict]
TelegramCallback = Callable[[telegram.Bot, telegram.update.Update, str, int], TelegramCallbackReturn]

message_callbacks: List[TelegramCallback] = []


def send_message(bot: telegram.Bot, update: telegram.update.Update, message_text: str):
    if len(message_text) <= telegram.MAX_MESSAGE_LENGTH:
        bot.send_message(chat_id=update.message.chat_id, text=message_text)
    else:
        bot.send_message(chat_id=update.message.chat_id, text=message_text[:telegram.MAX_MESSAGE_LENGTH - 4] + '\n...')
        bot.send_message(chat_id=update.message.chat_id, text='... mensagem truncada')


def test_parameter(function_: Callable[..., Any], name: str, paramtype):
    signature = inspect.signature(function_)
    try:
        if signature.parameters[name].annotation != paramtype:
            raise AttributeError(f"""The parameter {name} of the callback must be a {paramtype}
            Got {signature.parameters[name]}""")
    except KeyError:
        pass


def type_check(f: Callable[..., Any]):
    if not inspect.isfunction(f):
        raise AttributeError("The callback must be a function")
    test_parameter(f, "bot", telegram.Bot)
    test_parameter(f, "update", telegram.update.Update)
    test_parameter(f, "user", int)
    test_parameter(f, "message", str)


def callback_decorator_generator(
        name: str,
        activation_predicate: Callable[[telegram.Bot, telegram.update.Update, str, int], bool]
) -> Callable[[TelegramCallback], TelegramCallback]:
    def func(f: TelegramCallback) -> TelegramCallback:
        type_check(f)

        @wraps(f)
        def wrapper(bot: telegram.Bot, update: telegram.update.Update, message: str, user: int):
            logging.debug(f'Trying to call {name} callback')
            if activation_predicate(bot, update, message, user):
                logging.debug(f'Using {name} decorator')
                return f(bot, update, message, user)
            else:
                return ''

        message_callbacks.append(wrapper)
        return wrapper

    return func


directmessage = callback_decorator_generator(
    'direct message',
    lambda bot, update, message, user: (
        (isbotmetioned(message, bot.first_name, bot.name) or
        isprivatemessage(update)) and
        user_callbacks.isvaliduser(user)
    )
)

hearall = callback_decorator_generator(
    'heard',
    lambda bot, update, message, user: True)


@directmessage
def command_message(bot: telegram.Bot, update: telegram.update.Update, message: str, user: int) \
        -> TelegramCallbackReturn:
    return docparse.run_command(bot, update, message, user)


def message_callback(bot: telegram.Bot, update: telegram.update.Update) -> None:
    try:
        user_id = update['message']['from_user']['id']
    except KeyError:
        logging.error("Malformed JSON")
        return
    processed = update.message.text.strip()
    for callback in message_callbacks:
        messages = callback(bot, update, processed, user_id)
        process_message(bot, messages, update)


def send_file(bot: telegram.Bot, update: telegram.update.Update, name: str, content: str, file_type: str):
    f = BytesIO(bytes(content, 'utf-8'))
    bot.send_document(
        chat_id=update.message.chat_id,
        document=f,
        filename=name
    )


def send_image(bot: telegram.Bot, update: telegram.update.Update, content: str):
    try:
        bytes_ = base64.b64decode(content, validate=True)
    except binascii.Error:
        logging.error('Failed to decode base64 image')
        return
    f = BytesIO(bytes_)
    bot.send_photo(
        chat_id=update.message.chat_id,
        photo=f
    )


def process_message(bot: telegram.Bot, messages: Iterable[Dict], update: telegram.update.Update):
    for message in messages:
        if message['type'] == 'print':
            if message['content']:
                try:
                    send_message(bot, update, message['content'])
                except TelegramError:
                    logging.exception(
                        f"Error sending message \"{message['content']}\" in response to"
                        f' {update.message.text}')
                except Exception as err:
                    logging.exception(f'Unknown exception {err}')
            else:
                logging.warning(
                    f'Produced empty message in response to'
                    f' {update.message.text}')
        elif message['type'] == 'file':
            try:
                send_file(bot, update, message['name'], message['content'], message['file-type'])
            except TelegramError:
                logging.exception(
                    f"Error sending message \"{message['content'][:1024]}\" in response to"
                    f' {update.message.text}')
            except Exception as err:
                logging.exception(f'Unknown exception {err}')
        elif message['type'] == 'image':
            try:
                send_image(bot, update, message['content'])
            except TelegramError:
                logging.exception(
                    f"Error sending message \"{message['content'][:1024]}\" in response to"
                    f' {update.message.text}')
            except Exception as err:
                logging.exception(f'Unknown exception {err}')


def timed_message(bot: telegram.Bot, job: Job):
    for i in user_callbacks.external_messages():
        bot.send_message(chat_id=i['chat_id'],
        text=f'{i["sender"]}: {text_util.replace_message_emoji(i["text"])}')


def process_schedule(bot: telegram.Bot, job: Job):
    logging.debug('Processing schedules')
    update = telegram.Update(
        -1,
        message=telegram.Message(
            -1,
            -1,
            datetime.datetime.now(),
            telegram.Chat(settings.DEFAULT_CHANNEL, 'group')))
    for messages in scheduler.process_schedule_now(bot):
        process_message(bot, messages, update)
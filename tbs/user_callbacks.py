"""
Stub user_callbacks.py module, use it as a basis for your own callback code.
Make sure to fill the isvaliduser, isowner, isadmin with code that actually
checks if the user with the provided telegram id is authorized to run the code.

External messages is a function that should returns messages that were sent from
outside the robot to be print by the robot to the default channel.
"""

import logging
import sys
from typing import Iterable, Sequence, Union, Dict

import importlib
from .settings import CALLBACKS_MODULE

def isvaliduser(user: int) -> bool:
    logging.warning('isvaliduser is a stub')
    return True


def isowner(user: int) -> bool:
    logging.warning('isowner is a stub')
    return True


def isadmin(user: int) -> bool:
    logging.warning('isadmin is a stub')
    return True


def external_messages() -> Iterable[Dict[str, Union[str, str, int]]]:
    """Returns an iterable of dictionaries with the form:
    [{"chat_id":chat_id, "sender": sender, "text": text}, ...]
        chat_id: int - The id of the channel you are trying to send a message to
                         (can also be an user id).

        sender:  str - Service that sent the message.

        text:    str - Body of the message."""
    logging.warning('external_messages is a stub')
    return []


def on_valid_message(message: str, user: int):
    logging.warning('on_valid_messages is a stub')


def setup_callbacks():
    if CALLBACKS_MODULE is None:
        return
    for name, value in globals().items():
        if name.startswith('_') or name in ('CALLBACKS_MODULE', 'setup_callbacks'):
            pass
        else:
            try:
                mod = importlib.import_module(CALLBACKS_MODULE)
                new_value = getattr(mod, name, value)
                setattr(sys.modules[__name__], name, new_value)
            except ImportError as err:
                logging.error(f'Error importing the callbacks module {str(err)}')
                exit(-1)

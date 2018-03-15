import telegram

from tbs import user_callbacks
from .utils import bot_aliases


def isprivatemessage(update: telegram.update.Update) -> bool:
    return update['message']['chat']['type'] == 'private'


def isbotmetioned(message: str, botname: str, botusername: str) -> bool:
    firstword = message.strip().split(' ', 1)[0]
    names = bot_aliases(botname)
    return firstword in (names + [botusername])


def validate_acl(acl: str, bot: telegram.Bot, update: telegram.update.Update, message: str, user: int) -> bool:
    admin = user_callbacks.isadmin(user)
    owner = user_callbacks.isowner(user)
    private = isprivatemessage(update)
    direct = isbotmetioned(message, bot.first_name, bot.name)
    return eval(acl)

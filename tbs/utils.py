import telegram
from typing import List


def user_name(update: telegram.update.Update) -> str:
    return update.message.from_user['first_name'] + ' ' + update.message.from_user['last_name']


def bot_aliases(botname: str) -> List[str]:
    underscored = botname.replace("'", "").replace(" ", "_").lower()
    return [underscored, underscored.replace('_', ''), botname]

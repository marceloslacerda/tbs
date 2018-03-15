emoji_table = [
    (':smile:', '😄'),
    (':frowning:', '😞'),
    (':ghost:', '👻')
]


def replace_message_emoji(message: str) -> str:
    for t in emoji_table:
        message = message.replace(*t)
    return message


#!/usr/bin/env sh

import json
from io import StringIO

import requests

from clize import run, ArgumentError


def get_lipsum(amount=5, what='paragraphs', start=True):
    """Generates ipsum lorem content

    :param amount: The number of tokens to generate
    :param what: The type of token (paragraphs, words, characters, bytes or lists)
    :param start: Should the text start with "Lorem ipsum dolor sit amet..."
    """
    if what not in ('paragraphs', 'words', 'characters', 'bytes', 'lists'):
        raise ArgumentError(f'{what} is not a valid token')
    what = 'paras' if what == 'paragraphs' else what
    params = {
        'start': start,
        'what': what,
        'amount': amount
    }
    text = requests.get('https://lipsum.com/feed/json', params=params).text
    obj = json.loads(text)
    return obj['feed']['lipsum']


if __name__ == '__main__':
    out = StringIO()
    run(get_lipsum, exit=False, out=out, err=out)

    print(json.dumps({
        'type': 'file',
        'file-type': 'text',
        'name': 'lipsum.txt',
        'content': out.getvalue()
    }))
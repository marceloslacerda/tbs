import logging
import os


def get_int_variable(name, default):
    try:
        return int(os.environ.get(name, default))
    except ValueError:
        print(f'Failed to convert {name} to integer')


try:
    TOKEN = os.environ['TOKEN']
except KeyError:
    print(f'Variable TOKEN unset please read the README for instructions'
          f' on how to run tbs.')

DEFAULT_TIMEOUT = get_int_variable('TIMEOUT', 10)
MAX_PROCESS_OUTPUT = get_int_variable('MAX_PROCESS_OUTPUT', 10 * 1024 * 1024)  # 10MB

try:
    LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'DEBUG'))
except AttributeError:
    print(f'Could not use log level {os.environ["LOGLEVEL"]}')
CALLBACKS_MODULE = os.environ.get('CALLBACKS_MODULE', None)
STRING_MODULE = os.environ.get('STRING_MODULE', None)
try:
    DEFAULT_CHANNEL = os.environ['DEFAULT_CHANNEL']
except KeyError:
    DEFAULT_CHANNEL = '999999'
    print('Some functionalities will not be available since a default channel'
          ' is not set')

import logging
import os


try:
    TOKEN = os.environ['TOKEN']
    CONNECTION_STRING = os.environ['CONNECTION_STRING']
    LOGLEVEL = getattr(logging, os.environ.get('LOGLEVEL', 'DEBUG'))
    DEFAULT_CHANNEL = os.environ['DEFAULT_CHANNEL']
    DEFAULT_TIMEOUT = int(os.environ.get('TIMEOUT', 10))
    STRING_MODULE = os.environ.get('STRING_MODULE', None)
    CALLBACKS_MODULE = os.environ.get('CALLBACKS_MODULE', None)
    MAX_PROCESS_OUTPUT = int(os.environ.get('MAX_PROCESS_OUTPUT', 10*1024*1024))
except KeyError as err:
    print(f'Variable {err.args[0]} unset please read the README for instructions'
          f'on how to run tbs.')
except ValueError:
    print('Failed to convert some variable to its correct type')
except AttributeError:
    print(f'Could not use log level {os.environ["LOGLEVEL"]}')

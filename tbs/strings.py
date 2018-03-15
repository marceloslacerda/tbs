import logging
import sys
import importlib
from .settings import STRING_MODULE

PRELUDE = '''
{robot_name}, also responds by {aliases}

usage: {alias} <command> [<args>...]

Commands:

'''
END = '\nUse {alias} <command> --help to know more'
INSUFFICIENT_PERMISSIONS_WARNING = (
    'The user {pretty_name} does not have enough permissions '
    'to run that command in this context. Necessary permissions: '
)
TIMEOUT_EXPIRED_MESSAGE = (
    "The command {command} took more than {timeout} seconds to respond")
COMMAND_NOUN = 'command'
ARGUMENTS_NOUN = 'args'
COMMAND_DOES_NOT_EXIST_MESSAGE = "The command {command} is not one of:\n"
STARTUP_MESSAGE = "Bot started up"
COMMAND_RETURN_SIZE_EXCEEDED = 'The command {command} has exceeded the output size of MAX_PROCESS_OUTPUT'
PROCESS_DECODE_ERROR = 'Error while decoding the command {command} output'
EXIT_STATUS_NON_ZERO = 'The command {command} finished with error code {error_code}'

def setup_strings():
    if STRING_MODULE is None:
        return
    try:
        mod = importlib.import_module(STRING_MODULE)
    except ImportError as err:
        logging.error(f'Error importing the string module {str(err)}')
        exit(-1)
    for name, value in globals().items():
        if name.startswith('_') or name == 'STRING_MODULE' or name != name.upper():
            pass
        else:
            new_value = getattr(mod, name, value)
            setattr(sys.modules[__name__], name, new_value)

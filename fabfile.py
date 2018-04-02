from fabric.api import local
from fabric.context_managers import shell_env
import tempfile

VIRTUALENV_DIRECTORY = '/usr/local/virtualenvs'


def test():
    with shell_env(
            TOKEN='123:df',
            LOGLEVEL='DEBUG',
            DEFAULT_CHANNEL='-123456',
            # STRING_MODULE='undefined.py',
    ):
        local('PYTHONPATH="$(pwd):$PYTHONPATH" python -m unittest discover')

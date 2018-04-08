from fabric.api import local
from fabric.context_managers import shell_env


def test():
    with shell_env(
            TOKEN='123:df',
            LOGLEVEL='DEBUG',
            DEFAULT_CHANNEL='-123456'
    ):
        local('PYTHONPATH="$(pwd):$PYTHONPATH" python -m unittest discover')

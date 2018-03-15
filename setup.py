#!/usr/bin/env python

from distutils.core import setup
from os import path
from tbs import __version__

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

with open(path.join(here, 'requirements.txt')) as f:
    requirements = [l.strip() for l in f]

setup(
    name='telegram bot scaffold',
    version=__version__,
    description='A python program for scripting telegram bots.',
    author='Marcelo Lacerda',
    author_email='marceloslacerda@gmail.com',
    url='https://github.com/marceloslacerda/tbs',
    entry_points={
        'console_scripts': [
            'run-tbs = tbs.main:main',
        ],
    },
    packages=['tbs'],
    long_description=long_description,
    license='BSD',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Robot :: Telegram Bot Scaffold',
        'License :: BSD',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='bot',
    install_requires=requirements,
)


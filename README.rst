TBS: Telegram bot scaffolding
=============================

*DEPRECATED* This code is no longer maintained.

TBS is a program/framework for building python bots for telegram.
It's built upon `python-telegram-bot
<https://github.com/python-telegram-bot/python-telegram-bot>`_. with added neat
functionalities to make it easier to create and extend the power of bots for
reporting and change the status of your systems.

Feature Support
---------------

- ACLs defines who can do what and where.
- Bot commands are just programs/scripts.
- Every command is logged in a database for auditing.
- Messaging mechanism allows other services to send messages through the robot.
- Complex objects(text files, images) can be sent through JSON.
- Commands chan be scheduled with a CRON syntax.

Requirements
------------

- python 3.6
- virtualenvwrapper or equivalent


Running
-------

There's an example repository with easy run instructions that you can adapt to
your needs `here <https://github.com/marceloslacerda/tbs>`_.


Environment variables
---------------------

Of all variables only ``TOKEN`` is obligatory.

- ``TOKEN``

  A token is essential to run a bot with Telegram.
  The Telegram developer guide provides `instructions on how to obtain a token <https://core.telegram.org/bots#3-how-do-i-create-a-bot>`_.

- ``DEFAULT_CHANNEL``

  When DEFAULT_CHANNEL variable is set, the bot may send messages to you
  whenever a specific event happens. Like when it logs in or when it captures a
  message with the user_callback.external_messages function.
  There's a
  `question on Stackoverflow how to obtain a channel id <https://stackoverflow.com/questions/36099709/how-get-right-telegram-channel-id>`_.

- ``DEFAULT_TIMEOUT``

  ``DEFAULT_TIMEOUT`` specifies how long the bot will wait (seconds) for a command
  to complete before killing it.
  Currently the bot only sends a ``SIGTERM`` to the lagging command, so if it
  requires some other signal, it's better to wrap it in a script that will send
  the appropriate signal.

  The default is 10 seconds.

- ``MAX_PROCESS_OUTPUT``

  This variable specifies the maximum output size in number of characters. If
  the limit is reached the bot attempts to kill the command, the same
  limitations as with ``DEFAULT_TIMEOUT`` apply.
  The default is 10 MB of ASCII text (approximately 10 billion characters).

- ``LOGLEVEL``

  The log level of the bot by default the bot will print ``DEBUG`` messsages. If
  in production it's recommended to set it to ``INFO``.

- ``CALLBACKS_MODULE``

  Set this to the name of a module in the ``PYTHONPATH`` to install some
  callbacks in the bot. Check the documentation of the module tbs.user_callbacks
  for instructions on how to use each function.

- ``STRING_MODULE``

  Set this to the name of a module in the ``PYTHONPATH`` to override the default
  messages of the bot for ones of your choice.


Command formats
---------------

Commands are nothing more than executable simple scripts, python or otherwise.

All communication happens through ``stdout`` and command arguments in other
words when you write in your chat:

mybot do_something arg1 arg2 ...

What the bot does is, either ``python -m scripts.do_something.py arg1 arg2 ...``
or ``./do_something arg1 arg2`` wherever you executed ``run-tbs``.

Everything that do-something prints in either ``stdout`` or ``stderr``
is sent through the bot.

Please be aware that since python scripts are executed as a module, those
scripts must be valid
`python identifiers<https://docs.python.org/3/reference/lexical_analysis.html#identifiers>`_.

Flags
-----

Commands can have flags that tbs uses to decides various aspects about the
command execution:

- ``acl`` : type str : default ``admin``

    Acl is interpreted as a boolean expression in other words ``admin or owner``
    means that the referring command can be executed by admins or owners,
    ``admin and private`` means that the command should only be executed by
    admins in a private channel.

    There's no concept of user hierarchy built into the robot so if you wish
    you must implement it with ``user_callbacks``.

    - **admin:** Set true when the user is admin.
    - **owner:** Set true when the user is owner.
    - **private:** Set true when sent through a private conversation.
    - **direct:** Set true when you call the bot by its name.


- ``timeout`` : type int : default ``DEFAULT_TIMEOUT``
    After ``timeout`` seconds the command is killed and a message is shown in
    the chat warning the user about the incident. Overrides ``DEFAULT_TIMEOUT``.

- ``schedule`` : type str : default ``None``
    Commands that set this variable are executed periodically in a similar
    manner to a task scheduled using cron.

- ``json_output`` : type Bool : default ``False``
    When set to true commands will be interpreted as JSON objects (useful for
    sending files).

JSON
----

The fields for the returned JSON object are as follows:

- ``type``: Self explanatory, the possible values are ``'file'`` or ``'image'``.
- ``file-type``: Self descriptive, the only possible value is ``'text'``.
- ``name``: The name of the file, used when ``'type' : 'file'``.
- ``content``: It's an ASCII string with the contents of the message when sending text files or a base64 encoded text.

Example command:
________________

.. code-block:: bash

    #!/bin/sh
    echo '{"type":"file", "file-type": "text", "content": "hello world" }'

License
-------

Copyright (C) 2018  Marcelo de Sena Lacerda <marceloslacerda@gmail.com>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>

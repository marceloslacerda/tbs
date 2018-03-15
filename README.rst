TBS: Telegram bot scaffolding
=============================


TBS is a program/framework for building python bots for telegram.
It's built upon `python-telegram-bot
<https://github.com/python-telegram-bot/python-telegram-bot>`_. with added neat functionalities to make it
easier to create and extend the power of bots for reporting and change the
status of systems.

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

This guide assumes that you will be running tbs on a linux machine with the
requirements already installed. Adapt any of this to your necessities.

.. code-block:: bash

    # create and cd to the project directory
    mkdir -p my-bot/scripts/
    cd my-bot
    #Create a virtual environment for your project
    mkvirtualenv -p /usr/local/bin/python3.6 my-bot-env
    # Install tbs
    pip install git+https://github.com/marceloslacerda/tbs.git
    # Check how to get your token here: https://core.telegram.org/bots#3-how-do-i-create-a-bot
    export TOKEN='your-telegram-token'
    export LOGLEVEL=DEBUG
    # See how to get the id of your channel here:
    # https://stackoverflow.com/questions/36099709/how-get-right-telegram-channel-id
    export DEFAULT_CHANNEL='-99999'
    # How long tbs should wait before killing your commands (seconds)
    export DEFAULT_TIMEOUT=10
    echo '#!/bin/sh' > scripts/hello.sh
    echo 'echo hello world :D' >> scripts/hello.sh
    chmod +x scripts/hello.sh
    # Add your bot as admin to the channel you want to use
    run-tbs

At this point the bot will accept connections from anyone
everywhere. Make sure to create a callbacks module based on the
user_callbacks.py modle and export the CALLBACKS_MODULE variable.

Now your bot should respond *hello world :D* when you send hello to it
through telegram.


Command formats
---------------

Commands are nothing more than simple python scripts or executables.

All communication happens through ``stdout`` and command arguments in other words when you
write in your chat:

mybot do-something arg1 arg2 ...

What the bot does is, either ``python do-something.py arg1 arg2 ...``
or ``./do-something arg1 arg2``
wherever you executed ``run-tbs``.

Everything that do-something prints in either ``stdout`` or ``stderr`` is displayed in the chat.

Flags
-----

Commands can have flags that tbs uses to decides various aspects about the command execution:

- ``acl`` : type str : default admin : Acl is interpreted as a boolean expression

    - **admin:** Set true when the user is admin.
    - **owner:** Set true when the user is owner.
    - **private:** Set true when sent through a private conversation.
    - **direct:** Set true when you call the bot by its name.

    (either exactly as you write or spaces replaced for underscore and single quotes removed)

- ``timeout`` : type int : default ``DEFAULT_TIMEOUT``
    After ``timeout`` seconds the command is killed and a message is shown in the chat warning the user about the incident.

- ``schedule`` : type str : default None
    Commands that set this variable are executed periodically in a similar manner to a task.
    scheduled using cron

- ``json_output`` : type Bool : default False
    When set to true commands will be interpreted as JSON objects (useful for sending files).

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

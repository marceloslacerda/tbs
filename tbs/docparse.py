import asyncio
import json

import logging
import shlex

import os.path
import re
import subprocess
import sys
from typing import Any, Dict, Union, Iterable, List, TypeVar, Tuple, Optional

import telegram

from tbs import acl
from tbs import strings
from tbs import user_callbacks

from . import settings
from . import utils
from .utils import user_name

SCRIPTS_MODULE = 'scripts'
PROJECT_ROOT = os.curdir
SCRIPTS_DIR = os.path.join(PROJECT_ROOT, SCRIPTS_MODULE)
PROCESS_TIMEOUT = 20
# todo replace dict for named tuple
commands: Dict[str, Dict] = {}


def generate_help(robot_name: str, aliases: List[str]) -> str:
    or_aliases = ', '.join(aliases)
    buff = strings.PRELUDE.format(robot_name=robot_name, aliases=or_aliases, alias=aliases[0])
    for i in sorted(commands):
        buff += '    ' + i + '\n'
    return buff + strings.END.format(alias=or_aliases)


def get_acl(text: str) -> str:
    return get_one_by_regex(r'^#?acl\s*=\s*[\"\'](.+)[\"\']\s*$', text, 'admin')


def get_json(text: str) -> bool:
    return get_one_by_regex(r'^#?json_output\s*=\s*True\s*$', text, False)


def get_timeout(text: str) -> float:
    return float(
        get_one_by_regex(r'^#?timeout\s*=\s*(\d+\.?\d*)\s*$',
                         text,
                         float(settings.DEFAULT_TIMEOUT)))


def get_schedule(text: str) -> Optional[str]:
    return get_one_by_regex(r'^#?schedule\s*=\s*[\"\'](.+)[\"\']\s*$', text, None)


T = TypeVar('T', str, bool, float, None)


def get_one_by_regex(expression: str, text: str, on_no_match: T) -> T:
    groups = re.findall(expression, text, re.MULTILINE)
    if len(groups) == 0:
        return on_no_match
    else:
        # noinspection PyTypeChecker
        return groups[0]


def subscribe_commands():
    if not os.path.isdir(SCRIPTS_DIR):
        raise OSError('Could not find scripts directory')
    for entry in os.scandir(SCRIPTS_DIR):
        if entry.is_file():
            filename, extension = os.path.splitext(entry.name)
            if extension == '.pyc' or filename == '__init__':
                pass
            elif os.access(entry.path, os.R_OK):
                with open(entry.path) as f:
                    script = f.read()

                commands[filename] = {
                    'path': entry.path,
                    'acl': get_acl(script),
                    'json': get_json(script),
                    'python': extension == '.py',
                    'timeout': get_timeout(script),
                    'schedule': get_schedule(script)
                }
            else:
                logging.warning(f'File {entry.name} in the scripts directory was skipped')


def build_messages(content: Union[Iterable[Dict[str, Any]], str]) -> Iterable[Dict[str, Any]]:
    if isinstance(content, str):
        return [{'type': 'print', 'content': content}]
    else:
        return content


def run_command(bot: telegram.Bot, update: telegram.update.Update, message: str, user: int) -> Iterable[Dict]:
    parsed = parse_message(message, bot.first_name, bot.name)
    if isinstance(parsed, str):
        return build_messages(parsed)
    else:
        attributes, command, arguments = parsed
    if not acl.validate_acl(attributes['acl'], bot, update, message, user):
        pretty_name = user_name(update)
        return build_messages(
            strings.INSUFFICIENT_PERMISSIONS_WARNING.format(pretty_name=pretty_name) +
            attributes['acl'])
    else:
        user_callbacks.on_valid_message(message, user)
        return build_messages(run_subprocess(command, arguments, user, attributes))


def is_subcommand_help(parts: List[str]) -> bool:
    if len(parts) == 2:
        return parts[0] in commands and parts[1] in ('--help', '-h')
    else:
        return False


def parse_message(message: str, botname: str, botusername: str) ->\
        Union[Tuple[Dict[str, Any], str, Dict[str, Any]], str]:
    # telegram auto-replaces -- with —
    message = message.replace('—', '--').strip()
    message = lower_message(message)
    if acl.isbotmetioned(message, botname, botusername):
        parts = shlex.split(message)
    else:
        parts = shlex.split(message)
    parts = parts[1:]
    subscribe_commands()
    if parts[0] in commands:
        arguments = {f'<{strings.COMMAND_NOUN}>': parts[0],
                     f'<{strings.ARGUMENTS_NOUN}>': parts[1:]}
        command = parts[0]
    elif parts[0] in ('--help', '-h'):
        return generate_help(botname, utils.bot_aliases(botname))
    else:
        return (strings.COMMAND_DOES_NOT_EXIST_MESSAGE.format(command=parts[0])
                + "\n".join(commands) + "\n" +
                generate_help(botname, utils.bot_aliases(botname)))

    return commands[command], command, arguments


def lower_message(message):
    buff = []
    open_quote = False
    for c in message:
        if c in '\'"':
            open_quote = not open_quote
        if not open_quote:
            c = c.lower()
        buff.append(c)
    message = ''.join(buff)
    return message


def run_subprocess(
        command: str,
        arguments: Dict[str, Any],
        user_id: int,
        properties: Dict[str, Any]
) -> Union[Iterable[Dict[str, str]], str]:
    my_env = os.environ.copy()
    my_env["TELEGRAM_USER"] = str(user_id)

    if properties['python']:
        runnable = [sys.executable, '-m', f'{SCRIPTS_MODULE}.{command}'] + arguments[f'<{strings.ARGUMENTS_NOUN}>']
    else:
        runnable = ([properties['path']]
                    + arguments[f'<{strings.ARGUMENTS_NOUN}>'])
    (process_output,
     return_code,
     timeout_end,
     has_more_end,
     process_error_end) = subprocess_result_popen(runnable, properties, my_env)
    if properties['json'] and not process_error_end:
        try:
            json_type = json.loads(process_output)
        except json.JSONDecodeError as err:
            json_type = [{
                'type': 'print',
                'content': strings.PROCESS_DECODE_ERROR.format(
                    command=command
                )}]
            logging.error(err)
        if isinstance(json_type, dict):
            json_type = [json_type]
        else:
            return json_type
    elif len(process_output) > 0:
        json_type = [{'type': 'print', 'content': str(process_output, 'utf-8')}]
    else:
        json_type = []

    if timeout_end:
        json_type.append({
            'type': 'print',
            'content': strings.TIMEOUT_EXPIRED_MESSAGE.format(
                command=command,
                timeout=properties['timeout'])
        })
    if has_more_end:
        json_type.append({
            'type': 'print',
            'content': strings.COMMAND_RETURN_SIZE_EXCEEDED.format(command=command)
            })
    if process_error_end:
        json_type.append({
            'type': 'print',
            'content': strings.EXIT_STATUS_NON_ZERO.format(
                command=command,
                error_code=return_code
            )
        })
    return json_type


def subprocess_result_popen(
        runnable: List[str],
        properties: Dict[str, Any],
        environment: Dict[str, str]
) -> Tuple[bytes, int, bool, bool, bool]:
    runnable.insert(0, 'timeout')
    runnable.insert(1, str(properties['timeout']))
    process_output = b''
    with subprocess.Popen(
            runnable,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT) as proc:
        while (
                len(process_output) <= settings.MAX_PROCESS_OUTPUT
                and proc.poll() is None
        ):
            process_output += proc.stdout.read(100)
        timeout_end = proc.returncode == 124
        has_more_end = proc.returncode is None and len(process_output) > settings.MAX_PROCESS_OUTPUT
        process_error_end = proc.returncode not in (0, 124)
        if not has_more_end:
            process_output += proc.stdout.read(settings.MAX_PROCESS_OUTPUT - len(process_output))
    return process_output, proc.returncode, timeout_end, has_more_end, process_error_end

def subprocess_result_async(
    runnable: List[str],
    properties: Dict[str, Any],
    environment: Dict[str, str]
) -> Tuple[bytes, int, bool, bool, bool]:
    async def get_subprocess(future: asyncio.Future):
        process = await asyncio.create_subprocess_exec(
            *runnable,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            env=environment
        )
        future.set_result(process)

    #async def get_output_return_code(
    #        process: asyncio.subprocess.Process,
    #        output_future: asyncio.Future
    #):
    #    output = await process.stdout.read(settings.MAX_PROCESS_OUTPUT)
    #    return_code = process.returncode
    #    output_future.set_result(output, return_code)

    loop = asyncio.get_event_loop()
    process_future = asyncio.Future()
    asyncio.ensure_future(get_subprocess(process_future))
    loop.run_until_complete(process_future)
    process = process_future.result()
    try:
        output = yield from asyncio.wait_for(
            process.read,
            properties['timeout'],
            settings.MAX_PROCESS_OUTPUT)
        return_code = process.returncode
        has_more_end = return_code is None and len(output) == settings.MAX_PROCESS_OUTPUT
        process_error_end = return_code is not None and return_code< 0
        return output, return_code, False, has_more_end, process_error_end
    except asyncio.TimeoutError:
        return b'', None, True, False, False

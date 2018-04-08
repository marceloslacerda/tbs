import unittest

from tbs import docparse
from tbs import utils
from test.scripts import python, cronned

BOTNAME = "Ro' Bot"
HEADER = "Ro' Bot, also responds by ro_bot, robot, Ro Bot, Ro' Bot"
acl = 'a or b'
json_output = True
test_script_python = 'python'


class DocParseTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        docparse.SCRIPTS_DIR = 'test/scripts/'
        docparse.SCRIPTS_MODULE = 'test.scripts'
        docparse.subscribe_commands()

    def test_commands_is_set(self):
        self.assertIn(test_script_python, docparse.commands)

    def test_generate_help(self):
        message = docparse.generate_help(BOTNAME, utils.bot_aliases(BOTNAME))
        footer = "Use ro_bot <command> --help to know more"
        self.assertIn(HEADER, message, 'message must contain a message')
        self.assertIn('Commands:', message, 'message must contain a commands section')
        self.assertIn(test_script_python, message, f'message must list command {test_script_python}')
        self.assertIn(footer, message, 'message must contain a footer')

    def test_generate_help_sorted(self):
        message = docparse.generate_help(BOTNAME, utils.bot_aliases(BOTNAME))
        idx_acl = message.index('acl')
        idx_cronned = message.index('cronned')
        self.assertGreater(idx_cronned, idx_acl)

    def test_parse_message_invalid_command(self):
        parsed = docparse.parse_message('ro_bot henlo', BOTNAME, 'robot_bot')
        self.assertIn('command henlo is not one of:',
                      parsed,
                      'message must have available commands'
                      )
        self.assertIn(test_script_python, parsed, f'message must have {test_script_python}')

    def test_parse_message_correct(self):
        parsed = docparse.parse_message(
            f'ro_bot {test_script_python} test-arg', BOTNAME, 'robot_bot')
        args = parsed[2]
        self.assertEqual(['test-arg'], args['<args>'])
        self.assertEqual(test_script_python, args['<command>'])

    def test_fullname_mention(self):
        parsed = docparse.parse_message(
            f'{BOTNAME} {test_script_python} test-arg', BOTNAME, 'robot_bot')
        args = parsed[2]
        self.assertEqual(['test-arg'], args['<args>'])
        self.assertEqual(test_script_python, args['<command>'])

    def test_parse_message_no_mention(self):
        parsed = docparse.parse_message(
            f'{test_script_python} test-arg', BOTNAME, 'robot_bot')
        self.assertNotIsInstance(parsed, str)
        args = parsed[2]
        self.assertEqual(['test-arg'], args['<args>'])
        self.assertEqual(test_script_python, args['<command>'])

    def test_run_subprocess(self):
        parsed = docparse.parse_message(f'ro_bot {test_script_python} test-arg', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertIn(
            python.output_message,
            docparse.run_subprocess(command, arguments, -1, properties)[0]['content'])

    def test_parse_subcommand_help(self):
        parsed = docparse.parse_message(f'ro_bot {test_script_python} --help', BOTNAME, 'robot_bot')
        args = parsed[2]
        self.assertEqual(dict, type(args), 'args must be a dict')
        self.assertEqual(['--help'], args['<args>'], 'args must contain --help')
        self.assertEqual(test_script_python, args['<command>'], f'command must be {test_script_python}')

    def test_run_subprocess_help(self):
        parsed = docparse.parse_message(f'ro_bot {test_script_python} --help', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertIn(
            python.help_message,
            docparse.run_subprocess(command, arguments, -1, properties)[0]['content'])

    def test_run_subprocess_help_dashdash_substitution(self):
        parsed = docparse.parse_message(f'ro_bot {test_script_python} —help', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertIn(
            python.help_message,
            docparse.run_subprocess(command, arguments, -1, properties)[0]['content'])

    def test_run_subprocess_no_python(self):
        parsed = docparse.parse_message('ro_bot shell', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertIn(
            'success',
            docparse.run_subprocess(command, arguments, -1, properties)[0]['content'])

    def test_message_only_help(self):
        parsed = docparse.parse_message('ro_bot --help', BOTNAME, 'robot_bot')
        self.assertIn(' --help to know more', parsed)
        self.assertNotIn('The command --help is not one of:', parsed)

    def test_run_subprocess_stderr(self):
        parsed = docparse.parse_message(f'ro_bot {test_script_python} -e', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertIn(python.error_message,
                      docparse.run_subprocess(command, arguments, -1, properties)[0]['content'])

    def test_parse_message_json(self):
        parsed = docparse.parse_message('ro_bot json', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertTrue(properties['json'])

    def test_get_acl(self):
        with open('test/scripts/acl.sh') as f:
            text = f.read()
            self.assertEqual('admin', docparse.get_acl(text))
        with open('test/test_docparse.py') as f:
            text = f.read()
            self.assertEqual(acl, docparse.get_acl(text))

    def test_is_subcommmand_help(self):
        self.assertTrue(docparse.is_subcommand_help(f'{test_script_python} --help'.split()))
        self.assertTrue(docparse.is_subcommand_help(f'{test_script_python} -h'.split()))
        self.assertFalse(docparse.is_subcommand_help([test_script_python]))
        self.assertFalse(docparse.is_subcommand_help(f'foobar -h'.split()))
        self.assertFalse(docparse.is_subcommand_help(f'{test_script_python} help'.split()))

    def test_run_subprocess_json(self):
        parsed = docparse.parse_message('ro_bot json', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        for obj in docparse.run_subprocess(command, arguments, -1, properties):
            self.assertEqual(obj['type'], 'print')
            self.assertEqual(obj['content'], 'success')

    def test_parse_message_timeout(self):
        parsed = docparse.parse_message('ro_bot timeout', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        from .scripts import timeout
        self.assertEqual(properties['timeout'], timeout.timeout)

    def test_parse_message_no_timeout(self):
        from tbs.settings import DEFAULT_TIMEOUT
        parsed = docparse.parse_message('ro_bot json', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(properties['timeout'], DEFAULT_TIMEOUT)

    def test_run_subprocess_timeout(self):
        parsed = docparse.parse_message('ro_bot timeout', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed

        error_message = list(docparse.run_subprocess(command, arguments, -1, properties))[0]['content']
        self.assertIn(f"{properties['timeout']} seconds", error_message)

    def test_run_subprocess_large_output(self):
        parsed = docparse.parse_message('ro_bot large_output', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        error_message = list(docparse.run_subprocess(command, arguments, -1, properties))[1]['content']
        self.assertIn("output size of MAX_PROCESS_OUTPUT", error_message)

    def test_parse_message_schedule(self):
        parsed = docparse.parse_message('ro_bot cronned', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(properties['schedule'], cronned.schedule)

    def test_parse_message_quotes_upcase(self):
        argument = 'someArg'
        parsed = docparse.parse_message(f'ro_bot cronned "{argument}"', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(arguments['<args>'][0], argument)
        parsed = docparse.parse_message(f'ro_bot cronned {argument}', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(arguments['<args>'][0], argument.lower())

    def test_parse_message_quotes_joined(self):
        argument = 'foo bar'
        parsed = docparse.parse_message(f'ro_bot cronned "{argument}"', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(arguments['<args>'][0], argument)

    def test_parse_message_no_schedule(self):
        parsed = docparse.parse_message('ro_bot python', BOTNAME, 'robot_bot')
        properties, command, arguments = parsed
        self.assertEqual(properties['schedule'], None)

    def test_build_messages(self):
        messages = docparse.build_messages('test')
        for message in messages:
            self.assertEqual('test', message['content'])
        docparse.build_messages([{'content': 'test'}])
        for message in messages:
            self.assertEqual('test', message['content'])


if __name__ == '__main__':
    unittest.main()

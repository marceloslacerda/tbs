import unittest
import datetime

import telegram

from tbs import scheduler
from tbs import docparse
from test.scripts.cronned import message as test_message_minute
from test.scripts.cronned_hourly import message as test_message_hour


class Bot(telegram.Bot):
    @property
    def id(self):
        return -1

    @property
    def first_name(self):
        return 'Ro'

    @property
    def last_name(self):
        return 'Bot'

    @property
    def username(self):
        return 'robot_bot'

class TestSchedulerCase(unittest.TestCase):
    def setUp(self):
        docparse.SCRIPTS_DIR = 'test/scripts/'
        docparse.SCRIPTS_MODULE = 'test.scripts'
        docparse.subscribe_commands()
        self.bot = Bot('123:df')

    @unittest.skip('too long')
    def test_execute(self):
        scheduler.set_schedules()
        messages = scheduler.execute('cronned.py', self.bot)
        for message in messages:
            self.assertIn(test_message_minute, message['content'])

    def test_process_schedule_one_minute(self):
        time = datetime.datetime.now() - datetime.timedelta(minutes=1)
        scheduler.set_schedules(start_time=time)
        messages_list = list(scheduler.process_schedule_now(self.bot))
        self.assertNotEqual(messages_list, [])
        for messages in messages_list:
            messages = list(messages)
            self.assertNotEqual(messages, [])
            for message in messages:
                self.assertIn(test_message_minute, message['content'])
        messages_iterable = scheduler.process_schedule_now(self.bot)
        self.assertEqual([], list(messages_iterable))

    @unittest.skip('too long')
    def test_process_schedule_one_hour(self):
        time = datetime.datetime.now() - datetime.timedelta(minutes=60)
        scheduler.set_schedules(start_time=time)
        messages_list = list(scheduler.process_schedule_now(self.bot))
        self.assertNotEqual(messages_list, [])
        for messages in messages_list:
            messages = list(messages)
            self.assertNotEqual(messages, [])
            for message in messages:
                if test_message_minute in message['content']:
                    pass
                else:
                    self.assertIn(test_message_hour, message['content'])
        #messages_iterable = scheduler.process_schedule_now(self.bot)
        #self.assertEqual([], list(messages_iterable))


if __name__ == '__main__':
    unittest.main()

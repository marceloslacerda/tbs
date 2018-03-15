import unittest

from tbs.text_util import replace_message_emoji


class TextUtilTestCase(unittest.TestCase):
    def test_replaceMessageEmoji(self):
        self.assertEqual(
            replace_message_emoji(':smile:'), '😄')
        self.assertEqual(
            replace_message_emoji(':frowning:'), '😞')
        self.assertEqual(
            replace_message_emoji(':ghost:'), '👻')

    def test_replaceMessageEmojiAll(self):
        self.assertEqual(replace_message_emoji(':smile::frowning::ghost:'), '😄😞👻')


if __name__ == '__main__':
    unittest.main()

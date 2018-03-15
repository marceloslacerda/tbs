import unittest
import tbs.strings
def setup_callbacks():
    pass


ARGUMENTS_NOUN = 'foobar'


class StringsTestCase(unittest.TestCase):
    def test_replace(self):
        old_noun = tbs.strings.ARGUMENTS_NOUN
        self.assertNotEqual(old_noun, ARGUMENTS_NOUN)
        tbs.strings.STRING_MODULE = __name__
        tbs.strings.setup_strings()
        new_noun = tbs.strings.ARGUMENTS_NOUN
        self.assertEqual(ARGUMENTS_NOUN, new_noun)


if __name__ == '__main__':
    unittest.main()

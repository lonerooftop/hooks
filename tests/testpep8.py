import unittest

import basetest

_EXAMPLE_CORRECT_FILE = "print('hello')\nprint('world')\n"
_EXAMPLE_INCORRECT_FILE = "print 'hello'\nprint  ('world')\n"
_EXAMPLE_CORRECT_FILE2 = "print('bye')\nprint('mars')\n"
_EXAMPLE_INCORRECT_FILE2 = "print('bye')\nprint  ('mars')\n"
_EXAMPLE_INCORRECT_FILE3 = "print('bye')\nx=a\n\nprint  ('mars')\n"


class PEP8Test(basetest.HookTestCase):
    def setUp(self):
        super(PEP8Test, self).setUp()
        self.createAndCommitFiles({
            "correctfile.py": _EXAMPLE_CORRECT_FILE,
            "incorrectfile.py": _EXAMPLE_INCORRECT_FILE,
        }, "check in base files")

    def testCorrectNewFile(self):
        self.add_python_file_to_index_with_content(_EXAMPLE_CORRECT_FILE)
        self.assert_pre_commit_hook_succeeds(["Pep8Check"])

    def testIncorrectNewFile(self):
        self.add_python_file_to_index_with_content(_EXAMPLE_INCORRECT_FILE)
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "E271 multiple spaces after keyword",
            ["Pep8Check"])

    def testModifyCorrectFile(self):
        self.add_file_to_index_with_content(_EXAMPLE_CORRECT_FILE2,
                                            "correctfile.py")
        self.assert_pre_commit_hook_succeeds(["Pep8Check"])
        self.add_file_to_index_with_content(_EXAMPLE_INCORRECT_FILE2,
                                            "correctfile.py")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "E271 multiple spaces after keyword",
            ["Pep8Check"])

    def testModifyInCorrectFile(self):
        self.add_file_to_index_with_content(_EXAMPLE_CORRECT_FILE2,
                                            "incorrectfile.py")
        self.assert_pre_commit_hook_succeeds(["Pep8Check"])
        self.add_file_to_index_with_content(_EXAMPLE_INCORRECT_FILE2,
                                            "incorrectfile.py")
        # should succeed, since a broken file is allowed to remain broken
        self.assert_pre_commit_hook_succeeds(["Pep8Check"])
        self.add_file_to_index_with_content(_EXAMPLE_INCORRECT_FILE3,
                                            "incorrectfile.py")
        # Now it should fail since there are more errors now
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "resulted in new errors, number F821, E225:",
            ["Pep8Check"])


def main():
    unittest.main()

if __name__ == '__main__':
    main()

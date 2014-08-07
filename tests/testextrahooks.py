import basetest
import unittest
import os

_EXAMPLE_CORRECT_FILE = "print 'hello'\nprint 'world'\n"
_EXAMPLE_INCORRECT_FILE = "print 'hello'\nprint  'world'\n"
_EXAMPLE_CORRECT_FILE2 = "print 'bye'\nprint 'mars'\n"
_EXAMPLE_INCORRECT_FILE2 = "print 'bye'\nprint  'mars'\n"


class ExtraHooksTest(basetest.HookTestCase):
    def setUp(self):
        super(ExtraHooksTest, self).setUp()
        self.createAndCommitFiles({
            "correctfile.py": _EXAMPLE_CORRECT_FILE,
            "incorrectfile.py": _EXAMPLE_INCORRECT_FILE,
        }, "check in base files")
        self.add_python_file_to_index_with_content(_EXAMPLE_CORRECT_FILE2)

    def testNotExecutableHook(self):
        with open(self.root + "/.git/hooks/pre-commit-test-corr", "w+b") as f:
            f.write("echo correct\n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "not executable",
            ["Pep8Check"])

    def testFailingHook(self):
        with open(self.root + "/.git/hooks/pre-commit-test-corr", "w+b") as f:
            f.write("echo correct\n")
        os.chmod(self.root + "/.git/hooks/pre-commit-test-corr", 0755)
        with open(self.root + "/.git/hooks/pre-commit-test-fail", "w+b") as f:
            f.write("exit(1)\n")
        os.chmod(self.root + "/.git/hooks/pre-commit-test-fail", 0755)
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "pre-commit-test-fail",
            ["Pep8Check"])

    def testCorrectHook(self):
        with open(self.root + "/.git/hooks/pre-commit-test-corr1", "w+b") as f:
            f.write("echo correct\n")
        os.chmod(self.root + "/.git/hooks/pre-commit-test-corr1", 0755)
        with open(self.root + "/.git/hooks/pre-commit-test-corr2", "w+b") as f:
            f.write("echo correct\n")
        os.chmod(self.root + "/.git/hooks/pre-commit-test-corr2", 0755)
        self.assert_pre_commit_hook_succeeds(["Pep8Check"])
        self.add_python_file_to_index_with_content(_EXAMPLE_INCORRECT_FILE2)
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "E271 multiple spaces after keyword",
            ["Pep8Check"])


def main():
    unittest.main()

if __name__ == '__main__':
    main()

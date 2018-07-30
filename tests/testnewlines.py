import basetest
import unittest

_EXAMPLE_WINDOWS_NEWLINES = "print 'hello'\r\nprint 'world'\r\n"
_EXAMPLE_WINDOWS_NEWLINES2 = "print 'hello'\r\nprint 'world'\r\nprint 'bye'\r\n"
_EXAMPLE_UNIX_NEWLINES = "print 'hello'\nprint 'world'\n"
_EXAMPLE_UNIX_NEWLINES2 = "print 'hello'\nprint 'world'\nprint 'bye'\n"
_EXAMPLE_MIXED_NEWLINES = "print 'hello'\nprint 'world'\r\n"


class NewLineTest(basetest.HookTestCase):
    def setUp(self):
        super(NewLineTest, self).setUp()
        self.createAndCommitFiles({
            "windowsnewlines.py": _EXAMPLE_WINDOWS_NEWLINES,
            "unixnewlines.py": _EXAMPLE_UNIX_NEWLINES,
            "mixednewlines.py": _EXAMPLE_MIXED_NEWLINES,
            }, "check in base files")

    def test_add_new_file(self):
        filename = "testme.py"
        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_WINDOWS_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "All newlines are windows",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_MIXED_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Lines: 2",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_UNIX_NEWLINES
            )
        self.assert_pre_commit_hook_succeeds(["ConsistentNewlines"])

    def test_modify_unix_newlines_file(self):
        filename = "unixnewlines.py"
        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_WINDOWS_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "All newlines are windows",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_MIXED_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Lines: 2",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_UNIX_NEWLINES2
            )
        self.assert_pre_commit_hook_succeeds(["ConsistentNewlines"])

    def test_modify_windows_newlines_file(self):
        filename = "windowsnewlines.py"
        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_UNIX_NEWLINES
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "All newlines are unix",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_MIXED_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Lines: 1",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_WINDOWS_NEWLINES2
            )
        self.assert_pre_commit_hook_succeeds(["ConsistentNewlines"])

    def test_modify_mixed_newlines_file_to_unix(self):
        filename = "mixednewlines.py"
        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_MIXED_NEWLINES + _EXAMPLE_UNIX_NEWLINES
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "mix of windows and unix",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_UNIX_NEWLINES + _EXAMPLE_UNIX_NEWLINES,
            )
        self.assert_pre_commit_hook_succeeds(["ConsistentNewlines"])

    def test_modify_mixed_newlines_file_to_windows(self):
        filename = "mixednewlines.py"
        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_MIXED_NEWLINES + _EXAMPLE_WINDOWS_NEWLINES,
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "mix of windows and unix",
            ["ConsistentNewlines"],
            )

        self.add_file_to_index_with_content(
            filename=filename,
            content=_EXAMPLE_WINDOWS_NEWLINES + _EXAMPLE_WINDOWS_NEWLINES,
            )
        self.assert_pre_commit_hook_succeeds(["ConsistentNewlines"])


def main():
    unittest.main()

if __name__ == '__main__':
    main()

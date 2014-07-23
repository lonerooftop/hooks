import basetest
import unittest


class CharacterTest(basetest.HookTestCase):
    def test_only_safe_characters(self):
        self.add_python_file_to_index_with_content(
            "print 'hello" + chr(130) + "world'\n"
            )
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "unsafe character",
            ["OnlySafeCharacters"],
            )

    def test_no_tabs(self):
        self.add_python_file_to_index_with_content(
            "if 1:\tprint 'hello world'\n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Tabs in file",
            ["NoTabs"],
            )

    def test_tabs_in_makefile(self):
        self.add_file_to_index_with_content("helloworld:\n\techo hello world",
                                            "Makefile")
        self.assert_pre_commit_hook_succeeds(["NoTabs"])

    def test_no_whitespace_end_of_line(self):
        self.add_python_file_to_index_with_content("print 'hello world' \n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Whitespace at the end of the line",
            ["NoEndOfLineWhitespace"],
            )

    def test_no_whitespace_end_of_line_correct(self):
        self.add_python_file_to_index_with_content("print 'hello world '\n")
        self.assert_pre_commit_hook_succeeds(["NoEndOfLineWhitespace"])

    def test_no_merge_conflict_start_markers(self):
        self.add_python_file_to_index_with_content("'''\n<<<<<<< HEAD\n'''\n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Merge conflict marker",
            ["NoMergeConflictMarkers"],
            )

    def test_no_merge_conflict_middle_markers(self):
        self.add_python_file_to_index_with_content("'''\n=======\n'''\n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Merge conflict marker",
            ["NoMergeConflictMarkers"],
            )

    def test_no_merge_conflict_end_markers(self):
        self.add_python_file_to_index_with_content(
            "'''\n>>>>>>> some other revision\n'''\n")
        self.assert_pre_commit_hook_fails_with_text_regexp(
            "Merge conflict marker",
            ["NoMergeConflictMarkers"],
            )

    def test_almost_merge_conflict_markers(self):
        self.add_python_file_to_index_with_content(
            "#>>>>>>> some other revision\n"
            "'''\n"
            "======= with extra content\n"
            "this <<<< is not a confilct marker\n"
            "'''\n"
            )
        self.assert_pre_commit_hook_succeeds(["NoMergeConflictMarkers"])


def main():
    unittest.main()

if __name__ == '__main__':
    main()

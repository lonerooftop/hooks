import basetest
import unittest
import os


class StashTest(basetest.HookTestCase):
    STASH_REGEX = "(^|\n)Stashing local changes"
    UNSTASH_REGEX = "(^|\n)Unstashing local changes"

    def create_mad_files_in_index(self):
        """
        creates one modified, one added and
        one deleted file and stages them
        """
        with open(self.existing1txt, 'a') as f:
            f.write("second line")
        addedfile = os.path.join(self.root, "addedfile.txt")

        with open(addedfile, 'a') as f:
            f.write("added file")
        self.git_add([self.existing1txt, addedfile])
        self.git_rm([self.existing2txt])

    def test_stash_not_done_if_not_needed(self):
        self.create_mad_files_in_index()
        (returncode, stdout, stderr) = self.run_precommit_hook()
        self.assertEqual(returncode, 0)
        self.assertNotRegexpMatches(stdout, self.STASH_REGEX)
        self.assertNotRegexpMatches(stdout, self.UNSTASH_REGEX)

    def test_stash_done_if_file_deleted(self):
        self.create_mad_files_in_index()
        os.remove(self.existing1txt)

        (returncode, stdout, stderr) = self.run_precommit_hook()
        self.assertEqual(returncode, 0)
        self.assertRegexpMatches(stdout, self.STASH_REGEX)
        self.assertRegexpMatches(stdout, self.UNSTASH_REGEX)

    def test_stash_done_if_file_modified(self):
        self.create_mad_files_in_index()
        with open(self.existing1txt, "a") as f:
            f.write("hello world\n")

        (returncode, stdout, stderr) = self.run_precommit_hook()
        self.assertEqual(returncode, 0)
        self.assertRegexpMatches(stdout, self.STASH_REGEX)
        self.assertRegexpMatches(stdout, self.UNSTASH_REGEX)

    def test_stash_done_if_file_added(self):
        self.create_mad_files_in_index()
        addedfile2 = os.path.join(self.root, "addedfile2.txt")
        with open(addedfile2, "w") as f:
            f.write("hello world\n")

        (returncode, stdout, stderr) = self.run_precommit_hook()
        self.assertEqual(returncode, 0)
        self.assertRegexpMatches(stdout, self.STASH_REGEX)
        self.assertRegexpMatches(stdout, self.UNSTASH_REGEX)


def main():
    unittest.main()

if __name__ == '__main__':
    main()

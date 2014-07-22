import unittest
import tempfile
import subprocess
import os
import shutil

_MYDIR = os.path.dirname(os.path.realpath(__file__))


class HookTestCase(unittest.TestCase):
    def git_add(self, filenames):
        subprocess.check_call(["git", "add"] + filenames, cwd=self.root)

    def git_rm(self, filenames):
        subprocess.check_call(["git", "rm", "-q"] + filenames, cwd=self.root)

    def git_commit_nocheck(self, message):
        subprocess.check_call(["git", "commit", "-nqm", message],
                              cwd=self.root)

    def add_python_file_to_index_with_content(self, content,
                                              filename="added.py"):
        self.add_file_to_index_with_content(content, filename)

    def add_file_to_index_with_content(self, content, filename):
        addedfile = os.path.join(self.root, filename)
        with open(addedfile, "w") as f:
            f.write(content)
        self.git_add([addedfile])

    def assert_pre_commit_hook_succeeds(self, testnames=[]):
        (returncode, stdout, stderr) = self.run_precommit_hook(testnames)
        self.assertEqual(returncode, 0,
                         "hook should have succeeded,"
                         "failed with output %s" % stdout)

    def assert_pre_commit_hook_fails_with_text_regexp(self, text_regexp,
                                                      testnames=[]):
        """
        runs pre-commit hook and assumes the hook will fail
        the text_regexp is used as a regexp to compare the stdout
        against
        """
        (returncode, stdout, stderr) = self.run_precommit_hook(testnames)
        self.assertNotEqual(returncode, 0,
                            "should have failed, output: %s" % stdout)
        self.assertRegexpMatches(stdout, text_regexp)

    def run_precommit_hook(self, testnames=[]):
        """
        runs the precommit hook,
        only runs the test specified by testname, or all tests if []
        returning a tuple
        (returncode, stdout, stderr)
        """
        cmd = [os.path.realpath(os.path.join(_MYDIR, '..', 'pre-commit'))]
        proc = subprocess.Popen(cmd + testnames, cwd=self.root,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        proc.wait()
        return (proc.returncode, proc.stdout.read(), proc.stderr.read())

    def setUp(self):
        self.root = tempfile.mkdtemp()
        subprocess.check_call(("git", "init", "-q"), cwd=self.root)
        self.existing1txt = os.path.join(self.root, "existing1.txt")
        self.existing2txt = os.path.join(self.root, "existing2.txt")
        for filename in (self.existing1txt, self.existing2txt):
            with open(filename, "w") as f:
                f.write("file %s\n" % filename)
        self.git_add([self.existing1txt, self.existing2txt])
        self.git_commit_nocheck("initial setup")

    def tearDown(self):
        shutil.rmtree(self.root)

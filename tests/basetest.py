import unittest
import tempfile
import subprocess
import os
import shutil

_MYDIR = os.path.dirname(os.path.realpath(__file__))


class HookTestCase(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(HookTestCase, self).__init__(*args, **kwargs)
        if not hasattr(self, "assertRegex"):
            self.assertRegex = self.assertRegexpMatches
            self.assertNotRegex = self.assertNotRegexpMatches

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
                         "failed with stdout: %s\nstderr: %s" % (
                             stdout, stderr))

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
        try:
            self.assertRegex(stdout, text_regexp)
        except AssertionError as e:
            print("Stderr: %s" % stderr)
            raise e

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
        stdout = proc.stdout.read()
        proc.stdout.close()
        stderr = proc.stderr.read()
        proc.stderr.close()
        return (proc.returncode, stdout.decode("UTF-8"),
                stderr.decode("UTF-8"))

    def setUp(self):
        self.root = tempfile.mkdtemp()
        subprocess.check_call(("git", "init", "-q"), cwd=self.root)

    def createAndCommitFiles(self, files, message):
        """
        files is a dictionary of filename:content
        creates the files and commits them without
        running any checks
        message is the commit message
        """
        if len(files):
            for filename in files:
                self.add_file_to_index_with_content(
                    filename=filename,
                    content=files[filename]
                    )
        self.git_commit_nocheck(message)

    def tearDown(self):
        shutil.rmtree(self.root)

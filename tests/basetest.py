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

    def run_precommit_hook(self):
        """
        runs the precommit hook,
        returning a tuple
        (returncode, stdout, stderr)
        """
        cmd = os.path.realpath(os.path.join(_MYDIR, '..', 'pre-commit'))
        proc = subprocess.Popen(cmd, cwd=self.root,
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

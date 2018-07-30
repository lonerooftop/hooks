import os
import subprocess

from . import base
from . import filetype
from . import status


class CompileCheck(base.PerFileCheck):
    COMPILECOMMAND = []
    ONLY_IF_OLDFILE_COMPILES = True

    def checkOldFile(self, changedFile):
        with base.TempDir() as dirname:
            tempfilename = os.path.join(
                dirname,
                os.path.basename(changedFile.filename))
            with open(tempfilename, "w") as f:
                f.write("\n".join(changedFile.oldlines))
            cmd = list(self.COMPILECOMMAND)
            cmd.append(tempfilename)
            try:
                subprocess.check_output(cmd, stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError:
                return False
            return True

    def checkFile(self, changedFile):
        if changedFile.status != status.ADDED:
            if (self.ONLY_IF_OLDFILE_COMPILES and
                    not self.checkOldFile(changedFile)):
                # nothing to check, old file didn't compile
                return []

        cmd = list(self.COMPILECOMMAND)
        cmd.append(changedFile.filename)
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as calledprocesserror:
            return [base.CheckError(changedFile, self.__class__,
                                    calledprocesserror.output)]
        except OSError as e:
            error = (
                "Trying to execute:\n%s\n. This failed (%s), possibly "
                "executable is not installed on your system." % (
                    repr(cmd)[1:-1], str(e)))
            return [base.CheckError(changedFile, self.__class__, error)]
        return []


class PythonCompileCheck(CompileCheck):
    INTERESTED_IN_FILETYPES = [filetype.PYTHON]
    COMPILECOMMAND = ['python', '-m' 'py_compile']


class Pep8Check(CompileCheck):
    INTERESTED_IN_FILETYPES = [filetype.PYTHON]
    COMPILECOMMAND = ['flake8']

    def check_file_get_error_numbers(self, filename):
        cmd = list(self.COMPILECOMMAND) + [filename]
        try:
            output = subprocess.check_output(
                cmd, stderr=subprocess.STDOUT).decode("UTF-8")
        except subprocess.CalledProcessError as e:
            errornos = set()
            for line in e.output.decode("UTF-8").split("\n"):
                if line == "":
                    continue
                filenameandline, errorno, error = line.split(" ", 2)
                errornos.add(errorno)
            return (False, errornos, e.output.decode("UTF-8"), e.returncode)
        return (True, set(), output, 0)

    def checkFile(self, changedFile):
        if changedFile.status != status.ADDED:
            with base.TempDir() as dirname:
                tempfilename = os.path.join(
                    dirname,
                    os.path.basename(changedFile.filename))
                with open(tempfilename, "w") as f:
                    f.write("\n".join(changedFile.oldlines))
                _, old_errornos, _, _ = \
                    self.check_file_get_error_numbers(tempfilename)
        else:
            old_errornos = set()

        _, new_errornos, output, returncode = \
            self.check_file_get_error_numbers(changedFile.filename)

        cmd = list(self.COMPILECOMMAND) + [changedFile.filename]
        if returncode == 127:
            return [base.CheckError(
                changedFile, self.__class__,
                "Could not run %s, is it installed on the system?" % (
                    cmd, ))]

        extra_errornos = new_errornos - old_errornos
        if extra_errornos:
            return [base.CheckError(
                changedFile, self.__class__,
                "Running %s resulted in new errors, number %s:\n%s" % (
                    cmd, ", ".join(extra_errornos), output))]

        killed_errornos = old_errornos - new_errornos
        if killed_errornos:
            if new_errornos:
                print((
                    "You got rid of errors %s in %s, you deserve stars: " +
                    ("\U00002B50" * len(killed_errornos))) % (
                        ", ".join(killed_errornos),
                        changedFile.filename))  # noqa
            else:
                print((
                    "You got rid of all errors (%s) in %s, you deserve stars: "
                    "" + ("\U0001F31F" * len(killed_errornos))) % (
                        ", ".join(killed_errornos),
                        changedFile.filename))  # noqa
        return []

import base
import status
import filetype
import os
import subprocess


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
            except:
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
        return []


class PythonCompileCheck(CompileCheck):
    INTERESTED_IN_FILETYPES = [filetype.PYTHON]
    COMPILECOMMAND = ['python', '-m' 'py_compile']


class Pep8Check(CompileCheck):
    INTERESTED_IN_FILETYPES = [filetype.PYTHON]
    COMPILECOMMAND = ['flake8']

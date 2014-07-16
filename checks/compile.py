import base
import filetype
import os
import subprocess


class CompileCheck(base.PerFileCheck):
    COMPILECOMMAND = []
    EXTENSION = ''

    def checkFile(self, changedFile):
        cmd = self.COMPILECOMMAND
        extension = self.EXTENSION
        tmpname = base.tmpfile(changedFile.filename, extension)
        cmd.append(tmpname)
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as calledprocesserror:
            return [base.CheckError(changedFile, self.__class__,
                                    calledprocesserror.output)]
        finally:
            os.unlink(tmpname)
        return []


class PythonCompileCheck(CompileCheck):
    INTERESTED_IN_FILETYPES = [filetype.PYTHON]
    COMPILECOMMAND = ['python', '-m' 'py_compile']
    EXTENSION = '.py'

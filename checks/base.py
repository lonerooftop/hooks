import difflib
import subprocess
from . import status
from . import filetype
import tempfile
import shutil
import os


class ChangedFile(object):
    def __init__(self, filename, filetype, status):
        """filename is the name of the file relative to the base of the repo
        newlines is an array of all the lines in the new file
        newfilestring is a string with the full new file
        oldlines is an array of all the lines in the old file
        oldfilestring is a string with the full new file
        modifiedlinenumbers is an array of ints, that point to lines in the new
        file that were modified (0-based)"""

        self.filename = filename
        self.filetype = filetype
        self.status = status

        self._newlines = None
        self._newfilestring = None
        self._oldlines = None
        self._oldfilestring = None
        self._modifiedlinenumbers = None
        self._filediffset = False

    @property
    def newlines(self):
        self._getFileDiff()
        return self._newlines

    @property
    def newfilestring(self):
        self._getFileDiff()
        return self._newfilestring

    @property
    def oldlines(self):
        self._getFileDiff()
        return self._oldlines

    @property
    def oldfilestring(self):
        self._getFileDiff()
        return self._oldfilestring

    @property
    def modifiedlinenumbers(self):
        self._getFileDiff()
        return self._modifiedlinenumbers

    def _getFileDiff(self):
        """
        internal method to get the file diff only when its requested.
        It will probably error in cases that the file is not a UTF8 text file
        """
        if self._filediffset:
            return
        self._filediffset = True
        if self.status in (status.ADDED, status.MODIFIED):
            with open(self.filename, "rb") as f:
                newfilestring = f.read()
            self._newfilestring = newfilestring.decode("latin-1")
            self._newlines = newfilestring.split("\n")
        else:
            self._newfilestring = None
            self._newlines = None

        if self.status in (status.MODIFIED, status.DELETED):
            self._oldfilestring = subprocess.check_output(
                ("git", "show", "HEAD:%s" % self.filename)).decode("UTF-8")
            self._oldlines = self._oldfilestring.split("\n")
        else:
            self._oldfilestring = None
            self._oldlines = None

        if self.status == status.MODIFIED:
            self._modifiedlinenumbers = []
            diff = difflib.Differ().compare(self._oldlines, self._newlines)
            linenr = 0
            for line in diff:
                if line[0] in (' ', '+'):
                    linenr += 1
                if line[0] in ('+'):
                    self._modifiedlinenumbers.append(linenr-1)
        elif self.status == status.ADDED:
            self._modifiedlinenumbers = range(len(self._newlines))
        else:
            self._modifiedlinenumbers = None

    @classmethod
    def createForStagedFile(cls, filename):
        if not os.path.isfile(filename):
            # doesn't happen with regular paths, but may with submodules
            # for now we'll just ignore these
            return None
        textstatus = subprocess.check_output(
            ("git", "status", "--porcelain", filename)).decode("UTF-8")[0]
        filestatus = status.determineStatus(textstatus)

        return cls(filename, filetype.determineFiletype(filename), filestatus)


class CheckError:
    def __init__(self, changedFile, check, errormessage):
        self.changedFile = changedFile
        self.check = check
        self.errormessage = errormessage


class Check:
    """(abstract) base class for checker"""

    def __init__(self, changedFiles):
        self.changedFiles = changedFiles

    def doCheck(self):
        """should return the errors"""
        return []


class PerFileCheck(Check):
    """(abstract) base class to make a checker per file"""
    INTERESTED_IN_FILETYPES = filetype.TEXTFILES
    NOT_INTERESTED_IN_FILETYPES = []
    INTERESTED_IN_STATI = [status.ADDED, status.MODIFIED]

    def setupFileCheck(self, changedFile):
        # may be used by subclasses
        return

    def doCheck(self):
        errors = []
        for changedFile in self.changedFiles:
            self.setupFileCheck(changedFile)
            if self.interstedInFile(changedFile):
                errors += self.checkFile(changedFile)
        return errors

    def interstedInFile(self, changedFile):
        return (changedFile.status in self.INTERESTED_IN_STATI and
                changedFile.filetype in self.INTERESTED_IN_FILETYPES and
                changedFile.filetype not in self.NOT_INTERESTED_IN_FILETYPES)

    def checkFile(self, changedFile):
        return []


class PerModifiedLineCheck(PerFileCheck):
    def checkFile(self, changedFile):
        errors = []
        for linenr in changedFile.modifiedlinenumbers:
            line = changedFile.newlines[linenr]
            error = self.checkLine(line)
            if error:
                message = ["line %d: %s" % (linenr+1, error[0])]
                safeline = "".join([c if ord(c) < 128 else "?" for c in line])
                message.append(safeline)
                if len(error) > 0:
                    message.append("_" * error[1] + "^")
                fullmessage = "\n".join(message)
                error = CheckError(changedFile, self.__class__, fullmessage)
                errors.append(error)
        return errors

    def checkLine(self, line):
        """return (message, charnr) or None"""
        return None


class TempDir():
    def __enter__(self):
        self.tempdir = tempfile.mkdtemp()
        return self.tempdir

    def __exit__(self, errortype, value, traceback):
        shutil.rmtree(self.tempdir)


def check(checks_to_perform):
    cmd = ["git", "diff", "--cached", "--raw"]
    stati = subprocess.check_output(cmd).decode("UTF-8").split('\n')
    changedFiles = []
    for filestatus in stati[:-1]:  # last one is empty line
        filename = filestatus[39:]
        changedFile = ChangedFile.createForStagedFile(filename)
        if changedFile:
            changedFiles.append(changedFile)

    errors = []
    for check in checks_to_perform:
        checkinstance = check(changedFiles)
        errors += checkinstance.doCheck()
    return errors

import difflib
import subprocess
from . import status
from . import filetype
import tempfile
import shutil


class ChangedFile:
    def __init__(self, filename, filetype, status, newlines, newfilestring,
                 oldlines, oldfilestring, modifiedlinenumbers):
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
        self.newlines = newlines
        self.newfilestring = newfilestring
        self.oldlines = oldlines
        self.oldfilestring = oldfilestring
        self.modifiedlinenumbers = modifiedlinenumbers

    @classmethod
    def createForStagedFile(cls, filename):
        textstatus = subprocess.check_output(
            ("git", "status", "--porcelain", filename)).decode("UTF-8")[0]
        filestatus = status.determineStatus(textstatus)

        if filestatus in (status.ADDED, status.MODIFIED):
            with open(filename, "rb") as f:
                newfilestring = f.read()
            newfilestring = newfilestring.decode("latin-1")
            newlines = newfilestring.split("\n")
        else:
            newfilestring = None
            newlines = None

        if filestatus in (status.MODIFIED, status.DELETED):
            oldfilestring = subprocess.check_output(
                ("git", "show", "HEAD:%s" % filename)).decode("UTF-8")
            oldlines = oldfilestring.split("\n")
        else:
            oldfilestring = None
            oldlines = None

        if filestatus == status.MODIFIED:
            modifiedlinenumbers = []
            diff = difflib.Differ().compare(oldlines, newlines)
            linenr = 0
            for line in diff:
                if line[0] in (' ', '+'):
                    linenr += 1
                if line[0] in ('+'):
                    modifiedlinenumbers.append(linenr-1)
        elif filestatus == status.ADDED:
            modifiedlinenumbers = range(len(newlines))
        else:
            modifiedlinenumbers = None

        return cls(filename, filetype.determineFiletype(filename), filestatus,
                   newlines, newfilestring, oldlines, oldfilestring,
                   modifiedlinenumbers)


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
        changedFiles.append(changedFile)

    errors = []
    for check in checks_to_perform:
        checkinstance = check(changedFiles)
        errors += checkinstance.doCheck()
    return errors

import difflib
import subprocess
import status
import filetype
import tempfile
import shutil


class ChangedFile:
    def __init__(self, filename, filetype, status, newlines, oldlines,
                 modifiedlinenumbers):
        """filename is the name of the file relative to the base of the repo
        newlines is an array of all the lines in the new file
        oldlines is an array of all the lines in the old file
        modifiedlinenumbers is an array of ints, that point to lines in the new
        file that were modified (0-based)"""

        self.filename = filename
        self.filetype = filetype
        self.status = status
        self.newlines = newlines
        self.oldlines = oldlines
        self.modifiedlinenumbers = modifiedlinenumbers

    @classmethod
    def createForStagedFile(cls, filename):
        with open(filename, "r") as f:
            newlines = f.read().split("\n")
        oldlines = subprocess.check_output(
            ("git", "show", "HEAD:%s" % filename)).split("\n")

        textstatus = subprocess.check_output(
            ("git", "status", "--porcelain", filename))[0]

        filestatus = status.determineStatus(textstatus)
        modifiedlinenumbers = []

        diff = difflib.Differ().compare(oldlines, newlines)
        linenr = 0
        for line in diff:
            if line[0] in (' ', '+'):
                linenr += 1
            if line[0] in ('+'):
                modifiedlinenumbers.append(linenr-1)

        if filestatus == status.ADDED:
            oldlines = None
        if filestatus == status.DELETED:
            newlines = None
        return cls(filename, filetype.determineFiletype(filename), filestatus,
                   newlines, oldlines, modifiedlinenumbers)


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
    INTERESTED_IN_FILETYPES = filetype.TEXTFILES
    NOT_INTERESTED_IN_FILETYPES = []
    INTERESTED_IN_STATI = [status.ADDED, status.MODIFIED]

    """(abstract) base class to make a checker per file"""
    def doCheck(self):
        errors = []
        for changedFile in self.changedFiles:
            if self.interstedInFile(changedFile) and \
               changedFile.status in self.INTERESTED_IN_STATI and \
               changedFile.filetype in self.INTERESTED_IN_FILETYPES and \
               changedFile.filetype not in self.NOT_INTERESTED_IN_FILETYPES:
                errors += self.checkFile(changedFile)
        return errors

    def interstedInFile(self, changedFile):
        return True

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
                message.append(line)
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
    stati = subprocess.check_output(cmd).split('\n')
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

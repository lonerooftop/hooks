from . import base
from . import filetype


class OnlySafeCharacters(base.PerModifiedLineCheck):
    MESSAGE = "Detected unsafe character"
    SAFECHARS = set(['\t'] + [chr(i) for i in range(32, 127)])

    def checkLine(self, line):
        for i, c in enumerate(line):
            if c not in self.SAFECHARS:
                if c == "\r" and i == len(line) - 1:
                    # windows/unix enters have their own check
                    pass
                else:
                    return (self.MESSAGE, i)
        return None


class NoTabs(base.PerModifiedLineCheck):
    MESSAGE = "Tabs in file"
    NOT_INTERESTED_IN_FILETYPES = filetype.MAKEFILE

    def checkLine(self, line):
        pos = line.find('\t')
        if pos != -1:
            return (self.MESSAGE, pos)
        return None


class NoEndOfLineWhitespace(base.PerModifiedLineCheck):
    MESSAGE = "Whitespace at the end of the line"

    def checkLine(self, line):
        if len(line) > 0 and line[-1] == " ":
            return (self.MESSAGE, len(line)-2)
        return None


class NoMergeConflictMarkers(base.PerModifiedLineCheck):
    MESSAGE = "Merge conflict marker in file"

    def checkLine(self, line):
        if (line.startswith("<<<<<<< ") or
                line == ("=======") or
                line.startswith(">>>>>>> ")):
            return (self.MESSAGE, 0)
        return None

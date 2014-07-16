import base
import filetype
import re


class OnlySafeCharacters(base.PerModifiedLineCheck):
    MESSAGE = "Detected unsafe character"
    SAFECHARS = set(['\t'] + [chr(i) for i in range(32, 127)])

    def checkLine(self, line):
        for i, c in enumerate(line):
            if c not in self.SAFECHARS:
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
    REGEX = re.compile("\\s+$")

    def checkLine(self, line):
        pos = self.REGEX.search(line)
        if pos:
            return (self.MESSAGE, pos.start())
        return None

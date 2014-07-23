import base
import status

NEWLINE_UNIX = 1
NEWLINE_WINDOWS = 2
NEWLINE_CONSISTENT = 3

MESSAGE_WINDOWSFILE = ("Original file has windows newlines, please check in "
                       "with windows newlines.\n")
MESSAGE_UNIXFILE = "Windows newlines found, use unix newlines.\n"
MESSAGE_MIXEDFILE = (
    "The file was previously checked in with a mix of windows and unix "
    "newlines. Please fix this, by changing all newlines to the same sort. "
    "Think carefully about which of the two this should be."
    )


class ConsistentNewlines(base.PerFileCheck):
    """
    not making this a PerModifiedLineCheck
    since I'm interested in all lines
    and this is much faster
    """

    def checkFile(self, changedFile):
        if changedFile.status == status.ADDED:
            newlinetype = NEWLINE_UNIX
        else:
            oldnrwindowsnewlines = changedFile.oldfilestring.count("\r\n")
            oldnrnewlines = changedFile.oldfilestring.count("\n")
            oldnrunixnewlines = oldnrnewlines - oldnrwindowsnewlines

            if oldnrwindowsnewlines == 0:
                newlinetype = NEWLINE_UNIX
            elif oldnrunixnewlines == 0:
                newlinetype = NEWLINE_WINDOWS
            else:
                newlinetype = NEWLINE_CONSISTENT

        newnrwindowsnewlines = changedFile.newfilestring.count("\r\n")
        newnrnewlines = changedFile.newfilestring.count("\n")
        newnrunixnewlines = newnrnewlines - newnrwindowsnewlines

        if newlinetype == NEWLINE_UNIX:
            if newnrwindowsnewlines == 0:
                return []
            elif newnrunixnewlines == 0:
                return [base.CheckError(changedFile, self.__class__,
                                        MESSAGE_WINDOWSFILE +
                                        "All newlines are windows.")]
            else:
                pass
        elif newlinetype == NEWLINE_WINDOWS:
            if newnrunixnewlines == 0:
                return []
            elif newnrwindowsnewlines == 0:
                return [base.CheckError(changedFile, self.__class__,
                                        MESSAGE_WINDOWSFILE +
                                        "All newlines are unix.")]
            else:
                pass
        elif newlinetype == NEWLINE_CONSISTENT:
            if newnrwindowsnewlines == 0 or newnrunixnewlines == 0:
                return []
            else:
                return [base.CheckError(changedFile, self.__class__,
                                        MESSAGE_MIXEDFILE)]
        unixlinenumbers = []
        windowslinenumbers = []
        # ignore last line; it doesn't end in a newline (should
        # be the empty entry after the last newline)
        for (linenr, line) in enumerate(changedFile.newlines[:-1]):
            if len(line) == 0 or line[-1] != '\r':
                unixlinenumbers.append(linenr)
            else:
                windowslinenumbers.append(linenr)
        if newlinetype == NEWLINE_UNIX:
            return [base.CheckError(
                changedFile,
                self.__class__,
                MESSAGE_UNIXFILE +
                "Lines: %s" % ", ".join(
                    ["%d" % (i + 1) for i in windowslinenumbers]
                    )
                )]
        else:
            return [base.CheckError(
                changedFile,
                self.__class__,
                MESSAGE_WINDOWSFILE +
                "Lines: %s" % ", ".join(
                    ["%d" % (i + 1) for i in unixlinenumbers]
                    )
                )]

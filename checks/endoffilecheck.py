import base


class SingleNewlineEndOfFileCheck(base.PerFileCheck):
    def checkFile(self, changedFile):
        nrlines = len(changedFile.newlines)
        if nrlines < 1 or changedFile.newlines[-1] != "":
            return [base.CheckError(changedFile, self.__class__,
                    "No newline at the end of file")]
        if nrlines > 1 and changedFile.newlines[-2] == "":
            return [base.CheckError(changedFile, self.__class__,
                    "More than one newline at the end of file")]
        return []

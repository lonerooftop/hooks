import base


class SingleNewlineEndOfFileCheck(base.PerFileCheck):
    def checkFile(self, changedFile):
        if changedFile.newlines[-1] != "":
            return [base.CheckError(changedFile, self.__class__,
                    "No newline at the end of file")]
        if changedFile.newlines[-2] == "":
            return [base.CheckError(changedFile, self.__class__,
                    "More than one newline at the end of file")]
        return []

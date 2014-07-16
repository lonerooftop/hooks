import base


class SingleNewlineEndOfFileCheck(base.PerFileCheck):
    def checkFile(self, changedFile):
        content = base.getfile(changedFile.filename)
        if content[-1] != "\n":
            return [base.CheckError(changedFile, self.__class__,
                    "No newline at the end of file")]
        if content[-2] == "\n":
            return [base.CheckError(changedFile, self.__class__,
                    "More than one newline at the end of file")]
        return []

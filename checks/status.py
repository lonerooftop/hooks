MODIFIED = "Modified"
ADDED = "Added"
DELETED = "Deleted"


def determineStatus(statusflag):
    return {
        "M": MODIFIED,
        "A": ADDED,
        "D": DELETED,
        }[statusflag]

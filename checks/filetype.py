import ntpath

PYTHON = "python"
MAKEFILE = "Makefile"
CMAKE = "cmake"
CPP = "c++"
HPP = "c++ header"
SH = "shell script"
OTHER = "unknown filetype"

TEXTFILES = [
    PYTHON,
    MAKEFILE,
    CMAKE,
    CPP,
    HPP,
    SH,
    ]

_FILENAMEMATCH = {
    "Makefile": MAKEFILE,
    "CMakeLists.txt": CMAKE,
    }

_EXTENSIONMATCH = {
    "py": PYTHON,
    "cpp": CPP,
    "hpp": HPP,
    "sh": SH,
    }


def determineFiletype(filename):
    basename = ntpath.basename(filename)
    if basename in _FILENAMEMATCH:
        return _FILENAMEMATCH[basename]

    parts = basename.split(".")
    if len(parts) > 1:
        extension = parts[-1]
        if extension in _EXTENSIONMATCH:
            return _EXTENSIONMATCH[extension]
    return OTHER

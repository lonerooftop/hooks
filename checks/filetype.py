import ntpath

PYTHON = "python"
MAKEFILE = "Makefile"
CMAKE = "cmake"
CPP = "c++"
HPP = "c++ header"
H = "c header"
SH = "shell script"
PROTO = "Protocol buffers"
OTHER = "unknown filetype"

TEXTFILES = [
    PYTHON,
    MAKEFILE,
    CMAKE,
    CPP,
    HPP,
    H,
    SH,
    PROTO,
    ]

_FILENAMEMATCH = {
    "Makefile": MAKEFILE,
    "CMakeLists.txt": CMAKE,
    }

_EXTENSIONMATCH = {
    "py": PYTHON,
    "cpp": CPP,
    "hpp": HPP,
    "h": H,
    "sh": SH,
    "cmake": CMAKE,
    "proto": PROTO,
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

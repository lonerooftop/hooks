#!/usr/bin/python
import checks
import sys

CHECKS = [
    checks.compile.PythonCompileCheck,
    checks.compile.Pep8Check,
    checks.endoffilecheck.SingleNewlineEndOfFileCheck,
    checks.character.OnlySafeCharacters,
    checks.character.NoTabs,
    checks.character.NoEndOfLineWhitespace,
    ]


def main():
    errors = checks.check(CHECKS)

    if len(errors) > 0:
        for error in errors:
            print "%s, %s" % (error.changedFile.filename, error.errormessage)
        print "COMMIT FAILED, solve the problems and try again"
        sys.exit(1)

if __name__ == "__main__":
    main()

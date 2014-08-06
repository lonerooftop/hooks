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
    checks.character.NoMergeConflictMarkers,
    checks.newline.ConsistentNewlines,
    ]


def main():
    if len(sys.argv) > 1:
        # if called with commandline parameters, we assume
        # they are the names of the checks you want to run

        # This is how the tests work
        checks_to_run = []
        for checkname in sys.argv[1:]:
            newchecks = filter(lambda c: c.__name__ == checkname, CHECKS)
            if len(newchecks) == 1:
                checks_to_run += newchecks
            else:
                print("Check '%s' not found, aborting" % checkname)
                sys.exit(2)

    else:
        checks_to_run = CHECKS

    errors = checks.check(checks_to_run)

    if len(errors) > 0:
        for error in errors:
            print "%s, %s" % (error.changedFile.filename, error.errormessage)
        print "COMMIT FAILED, solve the problems and try again"
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/python
import argparse
import checks
import sys
import os
import subprocess

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
    gitrootdir = subprocess.check_output(
        ("git", "rev-parse", "--show-toplevel")).strip().decode("UTF-8")
    assert os.path.abspath(os.curdir) == gitrootdir, \
        "Please run the checks in the git root directory: %s " % gitrootdir
    parser = argparse.ArgumentParser()
    for check in CHECKS:
        name = check.__name__.lower()
        parser.add_argument(
            "--no-" + name,
            dest=check.__name__,
            action='store_false',
            help="Switch off check " + name)
    args = parser.parse_args()
    checks_to_run = []
    for check in CHECKS:
        if getattr(args, check.__name__):
            checks_to_run.append(check)

    errors = checks.check(checks_to_run)

    if len(errors) > 0:
        for error in errors:
            print(u"%s, %s" % (error.changedFile.filename, error.errormessage))
        print("COMMIT FAILED, solve the problems and try again")
        sys.exit(1)


if __name__ == "__main__":
    main()

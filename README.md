hooks
=====

I always feel that git checkins should be as clean as possible. There are multiple reasons for this, which I will not go into at this moment.

To ensure this I use a number of git hooks. The hooks are meant to be useful both on clean and on dirty repositories. Dirty in this case meaning that it already has plenty of checkins. Obviously we don't want to be forced to change whole files to comply if we just make some line changes (at some point you should do a history rewrite to fix all this).

The result should be that your repo is protected from getting more dirty (this also means that a clean repo stays clean).


# Usage

After installing the hook in your repo (see below), each checkin will be checked, and not allowed if it doesn't pass the tests.
To remove individual tests (forever), edit the pre-commit.py and remove the test.
To disable the hook forever, just remove the symlink /path/to/repo/.git/hooks/pre-commit.
To do a single commit without using the hook, do

    git commit -n ....

# Install

As far as I know, the current hooks only depend on one not-standard thing: the flake8 executable in your path. Installation is easy

    easy_install flake8

(or use another python package manager).

Alternatively you may disable the Pep8 check.

To install the hook in one repo, make a symlink from /path/to/repo/.git/hooks/pre-commit to the pre-commit executable in this repo.

To use the hook for all repo's, create a ~/.git-templates/hooks directory. Make a symlink from ~/.git-templates/hooks/pre-commit to /path/to/hooks/repo/pre-commit. Make sure the target link is absolute. Now enable this dir as your git-templates dir:

    git config --global init.templatedir '~/.git-template'

From now on any new repo (cloned or inited) will point to the hook. To enable the hook in an existing repo, run

    git init

in the existing repo (after making sure that there are no current hooks)

#Git stash and CowRamFS

During the hook we want to look at a version of the code that is about to be committed, not at the unstaged changes in git.
The current master does this by calling a sequence of git stash and git clean commands.
This works, but has three disadvantages: If the hook is interrupted, all one's local non-staged changes are stashed away; and secondly, any files created by the hooks that are in .gitignore are not being cleaned up.
Finally the editor will notice the file changing a couple of times, and not like this.

The alternative is to use CowRamFS (see the cowramfs branch). This works by overlaying a ram-based filesystem over the git repo.
CowRamFS is still exteremly alpha (was written by me over the course of a rainy Sunday afternoon), but seems to be doing the job. For those adventurous, try that branch!


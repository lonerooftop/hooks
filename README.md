hooks
=====

I always feel that git checkins should be as lcean as possible. There are multiple reasons for this, which I will not go into at this moment.

To ensure this I use a number of git hooks. The hooks are meant to be useful both on clean and on dirty repositories. Dirty in this case meaning that it already has plenty of checkins. Obviously we don't want to be forced to change whole files to comply if we just make some line changes (at some point you should do a history rewrite to fix all this).

The result should be that your repo is protected from getting more sirty (this also means that a clean repo stays clean).



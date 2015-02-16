from . import base
from . import compile
from . import newline
from . import endoffilecheck
from . import character

__all__ = [compile, endoffilecheck, character, newline, base]

check = base.check

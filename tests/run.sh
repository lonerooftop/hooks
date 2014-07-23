#!/bin/bash

python testlinechecks.py &&
    python teststash.py &&
    python testnewlines.py

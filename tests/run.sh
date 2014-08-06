#!/bin/bash

returnvalue=0

for mytest in test*.py; do
    echo "Running $mytest"
    python "$mytest"
    if [ $? -ne 0 ]; then
        returnvalue=1
    fi
done

exit $returnvalue

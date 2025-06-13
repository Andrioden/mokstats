#!/bin/sh

# UNIT TESTS (Disabled, no unittests atm)
#if pytest . -m unittest --quiet ; then
#    echo "python unit tests ok!"
#else
#    echo "python unit tests failed!"
#    exit 1
#fi

# VULTURE
if vulture . ; then
    echo "vulture ok!"
else
    echo "vulture failed! Will not commit."
    exit 1
fi

# ISORT
if isort . --check --quiet ; then
    echo "isort ok!"
else
    echo "isort failed! Will not commit."
    exit 1
fi

# BLACK
if black . --check --quiet ; then
    echo "black ok!"
else
    echo "black failed! Will not commit."
    exit 1
fi

# FLAKE8
if flake8 . ; then
    echo "flake8 ok!"
else
    echo "flake8 failed! Will not commit."
    exit 1
fi

# MYPY
if mypy . ; then
    echo "mypy ok!"
else
    echo "mypy failed! Will not commit."
    exit 1
fi

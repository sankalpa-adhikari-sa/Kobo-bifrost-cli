#!/bin/bash


export SKIP_BLACK=true
export SKIP_FLAKE8=true


echo "Running Tox with SKIP_BLACK, SKIP_FLAKE8, and SKIP_MYPY enabled..."
tox


if [ $? -eq 0 ]; then
    echo "Tox ran successfully!"
else
    echo "Tox failed. Please check the output for errors."
    exit 1
fi

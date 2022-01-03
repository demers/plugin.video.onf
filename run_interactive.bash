#!/bin/bash

export PYTHONPATH=$PWD

source tests-venv/bin/activate

echo running the following python program
echo $@
python3 -i "$@"

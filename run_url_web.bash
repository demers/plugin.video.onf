#!/bin/bash

export PYTHONPATH=$PWD

source tests-venv/bin/activate

echo running the following python program
echo -i url_web.py
python3 -i "url_web.py"

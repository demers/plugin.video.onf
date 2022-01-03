#!/bin/bash

sudo apt-get install -y python3-virtualenv

#virtualenv -p python3 tests-venv
python3 -m venv tests-venv

echo "Execute theses lines:"
echo "source tests-venv/bin/activate"

echo "pip install beautifulsoup4"
echo "pip install arrow"


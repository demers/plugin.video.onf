#!/bin/bash

export PYTHONPATH=$PWD
echo python path is: $PYTHONPATH

source tests-venv/bin/activate

#run unittest
python3 -m unittest discover -s tests -v -p test_*.py
if [ $? -ne 0 ]
then
	echo "unittest failed, aborting"
	exit 1
fi



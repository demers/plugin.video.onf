#!/bin/bash

cd ..
rm -f plugin.video.onf.zip
cd plugin.video.onf
cd ..
zip -r plugin.video.onf.zip plugin.video.onf/* -x "*tests-venv*" -x "*tests*" -x "*.bash" -x "*.pyo" -x "*__pycache__*" -x "*.init" -x "*.py.*"
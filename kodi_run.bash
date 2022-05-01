#!/bin/bash

MAIN=./main.py
URL_WEB=./url_web.py

if [[ -f "$MAIN" && -f "$URL_WEB" ]]; then
    /usr/bin/kodi
else
    echo "Les fichier main.py et url_web.py ne sont pas présents."
fi


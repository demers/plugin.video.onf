#!/bin/bash

MAINBAK=./main.py.bak
URL_WEB=./url_web.py.bak

if [[ -f "$MAIN" && -f "$URL_WEB" ]]; then
    /usr/bin/kodi
else
    mv main.py main.py.bak
    mv main_extended.py main.py
    mv url_web.py url_web.py.bak
    mv url_web_extended.py url_web.py
    /usr/bin/kodi
fi
mv main.py main_extended.py
mv main.py.bak main.py
mv url_web.py url_web_extended.py
mv url_web.py.bak url_web.py


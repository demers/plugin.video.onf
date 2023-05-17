#!/bin/bash

KODICONFIG=~/.kodi
MAIN=./main.py

source create_zip_release.bash
cp ./plugin.video.onf.zip $KODICONFIG
cd $KODICONFIG/addons/
unzip -o -u ../plugin.video.onf.zip

/usr/bin/kodi

if [[ -f "$KODICONFIG" && -f "$PLUGIN_KODI" ]]; then
else
    echo "Les fichier main.py et url_web.py ne sont pas présents."
fi


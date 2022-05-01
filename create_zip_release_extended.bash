#!/bin/bash

cd ..
rm -f plugin.video.onf.extended.zip
cd plugin.video.onf
mv main.py main.py.bak
mv main_extended.py main.py
mv url_web.py url_web.py.bak
mv url_web_extended.py url_web.py
cd ..
zip -r plugin.video.onf.extended.zip plugin.video.onf/addon.xml plugin.video.onf/fanart.jpg plugin.video.onf/icon.png plugin.video.onf/LICENSE plugin.video.onf/main.py plugin.video.onf/url_web.py
cd plugin.video.onf
mv main.py main_extended.py
mv main.py.bak main.py
mv url_web.py url_web_extended.py
mv url_web.py.bak url_web.py
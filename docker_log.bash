#!/bin/bash

# KODICONFIG=~/.kodi
KODICONFIG=~/.kodi.run

tac $KODICONFIG/temp/kodi.log | less

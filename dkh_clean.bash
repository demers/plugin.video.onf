#!/bin/bash
# Docker kodi headless

# Basé sur...
# https://github.com/matthuisman/docker-kodi-headless

echo Arrêt du conteneur...
docker stop kodi-headless
echo Suppression du conteneur...
docker rm kodi-headless

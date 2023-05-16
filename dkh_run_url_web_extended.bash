#!/bin/bash

# Basé sur...
# https://github.com/matthuisman/docker-kodi-headless

USERID=1000
GROUPID=1000
KODICONFIG=~/.kodi.test

docker ps | grep kodi-headless
echo ""

read -p "Réinitialisation du conteneur kodi-headless? (o/n) [n]" CHOIX
if [[ $CHOIX =~ ^[Oo]$ ]]
then
    echo Arrêt du conteneur...
    docker stop kodi-headless
    echo Suppression du conteneur...
    docker rm kodi-headless
    echo Démarrage du nouveau conteneur...
    docker run -d \
	--name=kodi-headless \
	-v ./:/prj \
	-v $KODICONFIG:/config/.kodi \
	-e PUID=$USERID \
	-e PGID=$GROUPID \
	-p 8080:8080 \
	-p 9090:9090 \
	-p 9777:9777/udp \
	matthuisman/kodi-headless:Nexus
	# matthuisman/kodi-headless:Matrix

    echo "Mise à jour APT..."
    docker exec kodi-headless bash -c "apt update"

    echo "Installation PIP3.."
    docker exec kodi-headless bash -c "apt install -y python3-pip"

    echo "Installation BS4..."
    docker exec kodi-headless bash -c "pip3 install beautifulsoup4"
fi

echo "Exécution des tests..."
docker exec -it kodi-headless bash -c "cd /prj; python3 -i url_web_extended.py"

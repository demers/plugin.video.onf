# Plugin Video Kodi Matrix pour ONF

Ce module vidéo permet de visionner les vidéos qui se trouvent sur le site
https://onf.ca

Le module offre 2 choix:

* Recherche
* Vidéos récents

Le premier permet de chercher par mots-clés dans la base de données du site
ONF.ca.  Le résultat est une liste de vidéos identique à ce qu'on obtient en
utilisant l'outil de recherche du site ONF.ca

Le deuxième fournit les 15 derniers vidéos ajoutées sur le site ONF.ca.  Le
résultat vient du fil RSS du site à https://www.onf.ca/fil-rss/ajouts-recents/

Le chargement se fait en moins d'une minute.

## Téléchargements Kodi

Voir la section *Releases* de Github pour télécharger les fichiers d'installation
ZIP pour Kodi Matrix.  Pas de version Leia (antérieure à Matrix) pour ce module.

## Version étendue

J'ai développé aussi une version étendue du module.  Cette version est stable mais
peut devenir non-fonctionnelle après un certain temps
parce que l'information est tirée du site ONF.ca qui change assez souvent.

Le module génère d'abord le menu en analysant la structure du site https://onf.ca
Le menu est sauvegardé localement dans le dossier du module.
La sauvegarde du menu est affiché par la suite.
La sauvegarde du menu est actualisée graduellement sur 10 jours.

Le chargement initial du module est long... autour de 45 minutes.  Par la suite, le chargement
est rapide (moins d'une minute) puisque l'information est archivée localement.

Voici le lien pour télécharger la version étendue du module
https://github.com/demers/plugin.video.onf/tree/main/extended


## Programmation

Le module a été développé à l'aide des scripts et modules suivants:

  * script.module.routing
  * script.module.beautifulsoup4


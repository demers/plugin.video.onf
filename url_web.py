# -*- coding: utf-8 -*-
# Free videos are provided by nfb.ca

import sys

# Python 3 versus Python 2
if ((3, 0) <= sys.version_info <= (3, 9)):
    # import urllib.parse
    from urllib.parse import urlparse
    # import urllib.request
    # from urllib.request import urlopen
    from urllib.request import Request, urlopen
elif ((2, 0) <= sys.version_info <= (2, 9)):
    from urlparse import urlparse
    # from urllib2 import urlopen
    from urllib2 import Request, urlopen


import os.path

# Import libraries to analyse Web pages
from bs4 import BeautifulSoup

import arrow
import os

import json
import hashlib

import re

import datetime

ADDON_ID = 'plugin.video.onf'

URL_PREFIXE = 'https://onf.ca'
URL_ADRESSE = URL_PREFIXE + '/index.php'

FICHIER_CATEGORIES = 'get_categories.json'
FICHIER_VIDEOS = 'get_videos_'  # On ajoutera sha1 et .json
FICHIER_VIDEOS_DOMAINS = 'list_url_domains.json'

NOMBRE_JOURS_DELAI_CATEGORIES = 14
NOMBRE_JOURS_DELAI_VIDEOS = 5

# Variable disponible tout au long de l'exécution du script
CATEGORIES_WITH_URL = []

# Section spéciale
TITRE_LA_COURBE = 'La Courbe | '

def strip_all(chaine):
    """
    Remove non-visible char beginning and end of string.
    Remove carriage return also.
    Remove spaces char beginning and end of string.
    """
    return chaine.replace('\t', '').replace('\n', '').replace('\r', '').strip(' ')

def verify_url_prefixe(chaine_url, prefixe_url):
    "Ajouter domaine http au début si non présent"
    if chaine_url[0:4] != 'http':
        return prefixe_url + chaine_url
    else:
        return chaine_url

def verify_url_video_inside(url):
    "Vérifier s'il y a au moins une vidéo sur une page"

    reponse_video = False

    # url_content= urlopen(url).read()
    url_content= read_url(url)
    liste_soup = BeautifulSoup(url_content, 'html.parser')

    job_a_element = liste_soup.find("a", class_="containerScreenshot")
    if job_a_element:
        reponse_video = True

    job_iframe_element = liste_soup.find('iframe', {'id': "player-iframe"})
    if job_iframe_element:
        reponse_video = True

    job_div_element = liste_soup.find('div', class_="banner")
    if job_div_element:
        reponse_video = True

    job_a_elements = liste_soup.find_all('a')
    for job_a_element in job_a_elements:
        job_img_element = job_a_element.find('img', class_="banner_image")
        if job_img_element:
            reponse_video = True

    return reponse_video

def read_url(url_text):
    "Chargement d'une page Web de façon sécuritaire"
    req = Request(url_text, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        url_content = urlopen(url_text).read()
    except:
        url_content = None

    return url_content

def extract_themes_la_courbe(url_principal):
    "Extraire les titres de la page La Courbe de l'ONF dans une liste de tuples (titre, url)"

    # url_content= urlopen(url_principal).read()
    url_content= read_url(url_principal)
    liste_soup = BeautifulSoup(url_content, 'html.parser')

    theme_tuple = []

    job_nav_elements = liste_soup.find_all("nav", class_="")
    for job_nav_element in job_nav_elements:
        job_a_elements = job_nav_element.find_all("a")
        for job_a_element in job_a_elements:
            if job_a_element.has_attr('data-introtab') and strip_all(job_a_element['data-introtab'])[0:5] == 'theme':
                theme_tuple.append((job_a_element.text, verify_url_prefixe(job_a_element['href'], URL_PREFIXE)))

    return theme_tuple

def get_categories(content_bs=None):
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.

    .. note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """

    # Variable disponible tout au long de l'exécution du script
    global CATEGORIES_WITH_URL

    chemin_fichier_cat = get_addondir() + FICHIER_CATEGORIES

    retour_categories_url = []
    if not check_file_older_than(chemin_fichier_cat, NOMBRE_JOURS_DELAI_CATEGORIES):
        retour_categories_url = load_dict(chemin_fichier_cat)
    else:

        if not content_bs:
            # url_content= urlopen(URL_ADRESSE).read()
            url_content= read_url(URL_ADRESSE)
            liste_soup = BeautifulSoup(url_content, 'html.parser')
        else:
            liste_soup = content_bs

        # Recherche de tous les liens qui contiennent un titre h2.
        job_a_elements = liste_soup.find_all("a")
        for job_a_element in job_a_elements:
            job_h2_elements = job_a_element.find_all("h2")
            for job_h2_element in job_h2_elements:
                url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
                if verify_url_video_inside(url_video):
                    retour_categories_url.append((strip_all(job_h2_element.text), url_video))
                # retour_categories_url.append((strip_all(job_h2_element.text),
                                        # verify_url_prefixe(job_a_element['href'], URL_PREFIXE)))

        # Recherche des sections avec carroussel dans la page.
        job_h2_elements = liste_soup.find_all("h2", class_="h3")
        for job_h2_element in job_h2_elements:
            if not job_h2_element.text in [category_tuple[0] for category_tuple in retour_categories_url]:
                job_href_element = job_h2_element.find("a")
                if job_href_element:
                    url_video = verify_url_prefixe(job_href_element['href'], URL_PREFIXE)
                    if verify_url_video_inside(url_video):
                        retour_categories_url.append((strip_all(job_href_element.text), url_video))

        # Recherche de la section 'Cinéma autochtone' présent en jan. 2022.
        job_a_element = liste_soup.find('a', {'id': "indigenousCinemaBanner"})
        if job_a_element and job_a_element.has_attr('href'):
            url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
            job_h2_element = job_a_element.find("h2", class_="h6")
            if job_h2_element:
                url_text = strip_all(job_h2_element.text)
            else:
                url_text = 'Inconnu'
            retour_categories_url.append((url_text, url_video))

        #soup.find_all('div', class_=lambda c: 'ABC' in c and 'BCD' in c and 'XYZ' not in c)

        # Recherche de la section 'La Courbe' de l'ONF présent en jan. 2022.
        job_a_elements = liste_soup.find_all("a", class_="m-curve-banner")
        for job_a_element in job_a_elements:
            if not job_a_element['href'] in [category_tuple[1] for category_tuple in retour_categories_url]:
                job_img_elements = liste_soup.find_all("img", class_="cb-logo")
                for job_img_element in job_img_elements:
                    url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
                    if verify_url_video_inside(url_video):
                        for (titre_theme, url_theme) in extract_themes_la_courbe(url_video):
                            retour_categories_url.append((TITRE_LA_COURBE + titre_theme, url_theme))
                            # retour_categories_url.append((strip_all(job_img_element['alt']), url_video))

        # Sauvegarde de la liste des catérogies avec les URL associés.
        save_dict(retour_categories_url, chemin_fichier_cat)

    CATEGORIES_WITH_URL = retour_categories_url
    return [category_tuple[0] for category_tuple in retour_categories_url]


def get_video_name_from_site(content_bs):
    "Extraire le titre de la vidéo"
    return_name = ''
    job_h1_element = content_bs.find("h1")
    if job_h1_element:
        return_name = strip_all(job_h1_element.text)
    return return_name

def get_video_url_from_site(content_bs):
    "Extraire l'URL de la vidéo"
    return_url = ''
    job_embed_element = content_bs.find('iframe', {'id': "player-iframe"})
    if job_embed_element:
        return_url = verify_url_prefixe(job_embed_element['src'], URL_PREFIXE)
    return return_url

def get_video_genre_from_site(content_bs):
    "Extraire le genre de la vidéo"

    return_genre = ''
    job_shortinfos_element = content_bs.find('div', class_="shortInfos")
    job_date_element = content_bs.find('span', class_="published")
    if job_shortinfos_element:
        return_genre += 'Réalisation: ' + strip_all(job_shortinfos_element.text)
    if job_date_element:
        return_genre += ' Date: ' + strip_all(job_date_element.text)

    return return_genre

def get_video_description_from_site(content_bs):
    "Extraire la description de la vidéo..."
    return_description = ''
    job_description_element = content_bs.find('div', {'id': "tabSynopsis"})
    if job_description_element:
        return_description = strip_all(job_description_element.text)
    return return_description

def get_video_thumb_from_site(content_bs):
    "Extraire l'image de la vidéo..."
    return_thumb = ''
    job_thumb_element = content_bs.find('link', {'rel': "image_src"})
    if job_thumb_element:
        return_thumb = job_thumb_element['href']
    return return_thumb

def get_videos_rss(content_bs):
    "Extraire les vidéos du fil RSS"

    return None

def get_videos(category):
    """
    Get the list of videofiles/streams.

    Here you can insert some parsing code that retrieves
    the list of video streams in the given category from some site or API.

    .. note:: Consider using `generators functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :param category: Category name
    :type category: str
    :return: the list of videos in the category
    :rtype: list
    """

    # Enlever le préfixe 'La Courbe' au début du nom de la catégorie
    # titre_category = category
    # if category[0:12] == TITRE_LA_COURBE:
        # titre_category = category

    chemin_fichier_videos = get_addondir() + FICHIER_VIDEOS + hashlib.sha1(category.encode('utf-8')).hexdigest() + '.json'
    retour_videos = []
    url_category = ''

    if not check_file_older_than(chemin_fichier_videos, NOMBRE_JOURS_DELAI_VIDEOS):
        retour_videos = load_dict(chemin_fichier_videos)
    else:

        # url_content = urlopen(URL_ADRESSE).read()
        url_content = read_url(URL_ADRESSE)
        liste_soup = BeautifulSoup(url_content, 'html.parser')

        # Vérifier si la variable de la liste des catégories n'est pas vide.
        if not CATEGORIES_WITH_URL:
            get_categories(liste_soup)
        if category in dict(CATEGORIES_WITH_URL):
            url_category = (dict(CATEGORIES_WITH_URL))[category]

        # Chargement seulement l'URL existe...
        if url_category:

            # Chargement de la page des vidéos...
            # url_content = urlopen(url_category).read()
            url_content = read_url(url_category)
            liste_soup_category = BeautifulSoup(url_content, 'html.parser')

            # La page contient plusieurs vidéos...
            job_a_elements = liste_soup_category.find_all("a", class_="containerScreenshot")
            for job_a_element in job_a_elements:
                video_group_element = dict()

                # Chargement de la page d'une vidéo...
                if job_a_element.has_attr('href'):
                    # url_content = urlopen(verify_url_prefixe(job_a_element['href'], URL_PREFIXE)).read()
                    url_content = read_url(verify_url_prefixe(job_a_element['href'], URL_PREFIXE))
                    if url_content:
                        liste_soup_video = BeautifulSoup(url_content, 'html.parser')
                        video_group_element['name'] = get_video_name_from_site(liste_soup_video)
                        video_group_element['video'] = get_video_url_from_site(liste_soup_video)
                        video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
                        video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
                        video_group_element['description'] = get_video_description_from_site(liste_soup_video)

                        print(video_group_element['name'])
                        retour_videos.append(video_group_element)

            # La page ne contient pas une liste de vidéos standards...
            # C'est le cas des vidéos de la section La Courbe...
            if not job_a_elements:

                job_a_elements2 = liste_soup_category.find_all('a')
                for job_a_element in job_a_elements2:
                    video_group_element = dict()
                    if job_a_element.has_attr('href'):
                        url_href = job_a_element['href']
                        job_img_element = job_a_element.find('img', class_="banner_image")
                        if job_img_element and urlparse(url_href).netloc.lower() == 'www.onf.ca':

                            # url_content = urlopen(verify_url_prefixe(url_href, URL_PREFIXE)).read()
                            url_content = read_url(verify_url_prefixe(url_href, URL_PREFIXE))
                            liste_soup_video = BeautifulSoup(url_content, 'html.parser')
                            video_group_element['name'] = get_video_name_from_site(liste_soup_video)
                            video_group_element['video'] = get_video_url_from_site(liste_soup_video)
                            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
                            video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
                            video_group_element['description'] = get_video_description_from_site(liste_soup_video)

                            retour_videos.append(video_group_element)

                        # Il n'y a pas d'image de type "banner_image" comme dans la section La Courbe
                        else:

                            # La page contient probablement qu'un seul vidéo...
                            video_group_element['name'] = get_video_name_from_site(liste_soup_category)
                            video_group_element['video'] = get_video_url_from_site(liste_soup_category)
                            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_category)
                            video_group_element['genre'] = get_video_genre_from_site(liste_soup_category)
                            video_group_element['description'] = get_video_description_from_site(liste_soup_category)

                            retour_videos.append(video_group_element)

        # Enlever les répétitions...
        # [dict(t) for t in {tuple(d.items()) for d in l}]
        # retour_videos = list(set(retour_videos))

        save_dict(retour_videos, chemin_fichier_videos)

    return retour_videos


def convert_video_path(path_video):
    """
    Convert path string to exact path string
    considering video type (Vimeo, Youtube, other).
    """

    return_path = ''

    # Chargement de la page des vidéos...
    # url_content = urlopen(path_video).read()
    url_content = read_url(path_video)
    liste_soup_video = BeautifulSoup(url_content, 'html.parser')

    job_script_elements = liste_soup_video.find_all("script")
    for job_script_element in job_script_elements:
        # re.search(r'meta\s*=\s*(.*?}])\s*\n', job_script_element.text)
        resultat_search = re.search(r"source\s*:\s*'(.*)'", job_script_element.text)
        if resultat_search:
            return_path = resultat_search[1]

    return return_path


def is_iterator(obj):
    "Verify if obj is an iterator type."
    if (
            hasattr(obj, '__iter__') and
            hasattr(obj, '__next__') and      # or __next__ in Python 3
            callable(obj.__iter__) and
            obj.__iter__() is obj
        ):
        return True
    else:
        return False


def get_addondir():
    """
    Get addon dir with standard functions.
    """
    # Ça devrait donner ce chemin:
    #   /home/ubuntu/.kodi/userdata/addon_data/plugin.video.horscine/

    try:
        import xbmc
        import xbmcaddon

        __addon__ = xbmcaddon.Addon(id=ADDON_ID)
        __addondir__ = xbmc.translatePath(__addon__.getAddonInfo('profile'))

        reponse = __addondir__

    except ImportError:
        # reponse = '/home/ubuntu/.kodi/userdata/addon_data/plugin.video.onf/'
        reponse = '/home/ubuntu/.kodi/userdata/addon_data/' + ADDON_ID + '/'

    if not os.path.exists(reponse):
        os.mkdir(reponse)

    return reponse

def check_file_older_than(fichier, jours):
    """
    Verify if file is old than a certain number of days.
    If file does not exist, the answer is true.
    """

    fichier_date = fichier + '.date'

    retour_bool = False
    if not os.path.isfile(fichier):
        retour_bool = True
    else:
        # criticalTime = arrow.now().shift(hours=+5).shift(days=-jours)
        # criticalTime = arrow.utcnow().shift(hours=+5).shift(days=-jours)
        criticalTime = arrow.utcnow().shift(days=-jours)
        # if os.stat(f).st_mtime < now - 7 * 86400:
        # itemTime = arrow.get(os.stat(fichier).st_mtime)
        try:
            file_date = open(fichier_date, 'r')
        except IOError:
            retour_bool = True
            return retour_bool
        finally:
            # itemTime = datetime.datetime.strptime(file_date.read(), "%d-%b-%Y (%H:%M:%S.%f)")
            itemTime = datetime.datetime.strptime(file_date.read(), "%Y-%m-%dT%H:%M:%S%z")

            # print('Temps du fichier: ' + str(itemTime))
            # print('Maintenant: ' + str(datetime.datetime.utcnow()))
            # print('criticalTime: ' + str(criticalTime))
            if itemTime < criticalTime:
                retour_bool = True
            file_date.close()
    return retour_bool

def save_dict(data_dict, fichier):
    """
    Save data structure dict in a file.
    """
    fichier_date = fichier + '.date'
    retour_reussite = True
    try:
        file = open(fichier, 'w')
        file_date = open(fichier_date, 'w')
    except IOError:
        retour_reussite = False
        return retour_reussite
    finally:
        file.write(json.dumps(data_dict, indent=4))
        # file_date.write(datetime.datetime.utcnow().strftime("%d-%b-%Y (%H:%M:%S.%f)"))
        # file_date.write(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S%z"))
        file_date.write(datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S-0000"))
        file.close()
        file_date.close()
        return retour_reussite

def load_dict(fichier):
    """
    Load data structure dict save in a file
    """
    struct_dict = dict()
    try:
        file = open(fichier, 'r')
    except IOError:
        file.close()
        return struct_dict
    finally:
        struct_dict = json.loads(file.read())
        file.close()
        return struct_dict


def get_list_search_results(keywordsearch):
    """
    Generate list results
    """

    # https://horscine.org/?s=test
    NOUV_URL_ADRESSE = URL_ADRESSE + '?s=' + keywordsearch
    # url_content= urllib.request.urlopen(NOUV_URL_ADRESSE).read()
    url_content= urlopen(NOUV_URL_ADRESSE).read()
    liste_soup = BeautifulSoup(url_content, 'html.parser')

    article_elements = liste_soup.find_all("article", class_="film")

    for article_element in article_elements:

        video_group_element = dict()
        job_h2_element = article_element.find("h2", class_="entry-title")
        href_element  = job_h2_element.find("a", {'rel': "bookmark"})

        # On récupère le contenu de la page de la vidéo...
        # url_content= urlopen(href_element['href']).read()
        url_content= read_url(href_element['href'])
        content_site_video_bs = BeautifulSoup(url_content, 'html.parser')

        video_name = get_video_name_from_site(content_site_video_bs)
        video_thumb = get_video_thumb_from_site(content_site_video_bs)
        video_url = get_video_url_from_site(content_site_video_bs)
        video_genre = get_video_genre_from_site(content_site_video_bs)
        video_description = get_video_description_from_site(content_site_video_bs)

        video_group_element['name'] = video_name
        video_group_element['thumb'] = video_thumb
        video_group_element['video'] = video_url
        video_group_element['genre'] = video_genre
        video_group_element['description'] = video_description
        yield video_group_element

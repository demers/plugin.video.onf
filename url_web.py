# -*- coding: utf-8 -*-
# Free videos are provided by nfb.ca

import sys

# Python 3 versus Python 2
if ((3, 0) <= sys.version_info <= (3, 9)):
    # import urllib.parse
    from urllib.parse import urlparse
    # import urllib.request
    from urllib.request import urlopen
elif ((2, 0) <= sys.version_info <= (2, 9)):
    from urlparse import urlparse
    from urllib2 import urlopen

import os.path

# Import libraries to analyse Web pages
from bs4 import BeautifulSoup

import arrow
import os

import json
import hashlib

import re

ADDON_ID = 'plugin.video.onf'

URL_PREFIXE = 'https://onf.ca'
URL_ADRESSE = URL_PREFIXE + '/index.php'

FICHIER_CATEGORIES = 'get_categories.json'
FICHIER_VIDEOS = 'get_videos_'  # On ajoutera sha1 et .json
FICHIER_VIDEOS_DOMAINS = 'list_url_domains.json'

NOMBRE_JOURS_DELAI_CATEGORIES = 13
NOMBRE_JOURS_DELAI_VIDEOS = 2

# Variable disponible tout au long de l'exécution du script
CATEGORIES_WITH_URL = []

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
            url_content= urlopen(URL_ADRESSE).read()
            liste_soup = BeautifulSoup(url_content, 'html.parser')
        else:
            liste_soup = content_bs

        # Recherche de tous les liens qui contiennent un titre h2.
        job_a_elements = liste_soup.find_all("a")
        for job_a_element in job_a_elements:
            job_h2_elements = job_a_element.find_all("h2")
            for job_h2_element in job_h2_elements:
                retour_categories_url.append((strip_all(job_h2_element.text),
                                        verify_url_prefixe(job_a_element['href'], URL_PREFIXE)))

        # Recherche des sections avec carroussel dans la page.
        job_h2_elements = liste_soup.find_all("h2", class_="h3")
        for job_h2_element in job_h2_elements:
            if not job_h2_element.text in [category_tuple[0] for category_tuple in retour_categories_url]:
                job_href_element = job_h2_element.find("a")
                if job_href_element:
                    retour_categories_url.append((strip_all(job_href_element.text),
                                            verify_url_prefixe(job_href_element['href'], URL_PREFIXE)))

        # Recherche de la section 'Cinéma autochtone' présent en jan. 2022.
        job_h2_elements = liste_soup.find_all("h2", class_="h6")
        for job_h2_element in job_h2_elements:
            if not job_h2_element.text in [category_tuple[0] for category_tuple in retour_categories_url]:
                job_href_element = job_h2_element.find("a")
                if job_href_element:
                    retour_categories_url.append((strip_all(job_href_element.text),
                                            verify_url_prefixe(job_href_element['href'], URL_PREFIXE)))

        #soup.find_all('div', class_=lambda c: 'ABC' in c and 'BCD' in c and 'XYZ' not in c)

        # Recherche de la section 'La Courbe' de l'ONF présent en jan. 2022.
        job_a_elements = liste_soup.find_all("a", class_="m-curve-banner")
        for job_a_element in job_a_elements:
            if not job_a_element['href'] in [category_tuple[1] for category_tuple in retour_categories_url]:
                job_img_elements = liste_soup.find_all("img", class_="cb-logo")
                for job_img_element in job_img_elements:
                    retour_categories_url.append((strip_all(job_img_element['alt']),
                                            verify_url_prefixe(job_a_element['href'], URL_PREFIXE)))

        # Sauvegarde de la liste des catérogies avec les URL associés.
        # save_dict(retour_categories_url, chemin_fichier_cat)

    CATEGORIES_WITH_URL = retour_categories_url
    # print(CATEGORIES_WITH_URL)
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
    # job_embed_element = content_bs.find('meta', {'property': "og:url"})
    job_embed_element = content_bs.find('iframe', {'id': "player-iframe"})
    if job_embed_element:
        return_url = verify_url_prefixe(job_embed_element['src'], URL_PREFIXE)
    return return_url

# A COMPLÉTER
def get_video_genre_from_site(content_bs):
    "Extraire le genre de la vidéo"

    return_genre = ''
    job_shortinfos_element = content_bs.find('div', class_="shortInfos")
    job_date_element = content_bs.find('span', class_="published")
    job_temps_element = content_bs.find('span', class_="duration duree")
    return_genre += 'Réalisation: ' + strip_all(job_shortinfos_element.text)
    return_genre += ' Date: ' + strip_all(job_date_element.text)
    # return_genre += ' Durée: ' + strip_all(job_temps_element.text)

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

# def get_all_sections(content_bs=None):
    # "Extraire les sections BeautifulSoup de la page"

    # if not content_bs:
        # # url_content= urllib.request.urlopen(URL_ADRESSE).read()
        # url_content= urlopen(URL_ADRESSE).read()
        # liste_soup = BeautifulSoup(url_content, 'html.parser')
    # else:
        # liste_soup = content_bs

    # list_categories = get_categories(liste_soup)
    # job_section_elements = liste_soup.find_all("section", class_="elementor-section")
    # for job_section_element in job_section_elements:
        # # Vérifier si un lien URL est présent dans cette section...
        # job_a_element = job_section_element.find("a")
        # # Vérifier si une "sous-section" est présente dans la section...
        # job_section_souselement = job_section_element.find("section")
        # # Vérifier si une vidéo est présente et s'il n'y a pas de "sous-section"...
        # if job_a_element and not job_section_souselement:
            # title_element = job_section_element.find("h2")
            # if title_element and strip_all(title_element.text) in list_categories:
                # yield job_section_element
    # return
    # yield


# def get_section_category(category, content_bs=None):
    # "Extraire la section BeautifulSoup de la page de la catégorie en paramètre"

    # if not content_bs:
        # # url_content= urllib.request.urlopen(URL_ADRESSE).read()
        # url_content= urlopen(URL_ADRESSE).read()
        # liste_soup = BeautifulSoup(url_content, 'html.parser')
    # else:
        # liste_soup = content_bs

    # retour_element = None
    # job_section_elements = liste_soup.find_all("section", class_="elementor-section")
    # if category in get_categories(liste_soup):
        # for job_section_element in job_section_elements:
            # # Vérifier si un lien URL est présent dans cette section...
            # job_a_element = job_section_element.find("a", class_="elementor-post__thumbnail__link")
            # # Vérifier si une "sous-section" est présente dans la section...
            # job_section_souselement = job_section_element.find("section", class_="elementor-section")
            # # Vérifier si une vidéo est présente et s'il n'y a pas de "sous-section"...
            # if job_a_element and not job_section_souselement:
                # title_element = job_section_element.find("h2", class_="elementor-heading-title elementor-size-default")
                # if title_element and strip_all(title_element.text) == category:
                    # retour_element = job_section_element
    # return retour_element

# def get_href_section(section_element):
    # "Get URL to href element in the section element"

    # if section_element != None:
        # job_a_elements = section_element.find_all("a", class_="elementor-post__thumbnail__link")
        # for job_a_element in job_a_elements:
            # if job_a_element.find('img'):
                # yield job_a_element['href']

# def exists_video_section_element(section_element):
    # "Check if exists video URL in the section element"

    # retour_bool = False
    # if section_element != None:
        # job_a_elements = section_element.find_all("a")
        # for job_a_element in job_a_elements:
            # if job_a_element.find('img', {'alt': "image du film"}):
                # retour_bool = True
    # return retour_bool


# def get_url_videos_site(section_element):
    # "Get URL to video sites in the section element"

    # if section_element != None:
        # job_a_elements = section_element.find_all("a")
        # for job_a_element in job_a_elements:
            # if job_a_element.find('img', {'alt': "image du film"}):
                # yield job_a_element['href']

# def get_content_video_site(url):
    # "Get content_bs containing iframe video section"

    # # url_content = urllib.request.urlopen(url).read()
    # url_content = urlopen(url).read()
    # liste_soup = BeautifulSoup(url_content, 'html.parser')

    # content_site_element = liste_soup.find("iframe")
    # if content_site_element:
        # yield liste_soup
    # else:
        # for video_site in get_url_videos_site(liste_soup):

            # # url_content = urllib.request.urlopen(video_site).read()
            # url_content = urlopen(video_site).read()
            # liste_soup2 = BeautifulSoup(url_content, 'html.parser')
            # content_site_element = liste_soup2.find("iframe")
            # if content_site_element:
                # yield liste_soup2

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

    chemin_fichier_videos = get_addondir() + FICHIER_VIDEOS + hashlib.sha1(category.encode('utf-8')).hexdigest() + '.json'
    retour_videos = []

    if not check_file_older_than(chemin_fichier_videos, NOMBRE_JOURS_DELAI_VIDEOS):
        retour_videos = load_dict(chemin_fichier_videos)
    else:

        url_content = urlopen(URL_ADRESSE).read()
        liste_soup = BeautifulSoup(url_content, 'html.parser')

        # Vérifier si la variable de la liste des catégories n'est pas vide.
        if not CATEGORIES_WITH_URL:
            get_categories(liste_soup)
        url_category = (dict(CATEGORIES_WITH_URL))[category]
        print('URL Category: ' + url_category)

        # Chargement de la page des vidéos...
        url_content = urlopen(url_category).read()
        liste_soup_category = BeautifulSoup(url_content, 'html.parser')

        # La page contient plusieurs vidéos...
        job_a_elements = liste_soup_category.find_all("a", class_="containerScreenshot")
        for job_a_element in job_a_elements:

            # Chargement de la page d'une vidéo...
            url_content = urlopen(job_a_element['href']).read()
            liste_soup_video = BeautifulSoup(url_content, 'html.parser')
            video_group_element = dict()
            # job_img_element = job_a_element.find("img")
            # video_group_element['name'] = job_img_element['alt']
            video_group_element['name'] = get_video_name_from_site(liste_soup_video)
            video_group_element['video'] = get_video_url_from_site(liste_soup_video)
            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
            video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
            video_group_element['description'] = get_video_description_from_site(liste_soup_video)

            retour_videos.append(video_group_element)

        # La page contient probablement qu'une seule vidéo...
        if not job_a_elements:
            video_group_element = dict()
            video_group_element['name'] = get_video_name_from_site(liste_soup_category)
            video_group_element['video'] = get_video_url_from_site(liste_soup_category)
            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_category)
            video_group_element['genre'] = get_video_genre_from_site(liste_soup_category)
            video_group_element['description'] = get_video_description_from_site(liste_soup_category)

            retour_videos.append(video_group_element)

        # job_section_element = get_section_category(category, liste_soup)

        # if not exists_video_section_element(job_section_element):
            # list_url_videos_site = []
            # for url_section in get_href_section(job_section_element):
                # # url_content = urllib.request.urlopen(url_section).read()
                # url_content = urlopen(url_section).read()
                # subsection_bs = BeautifulSoup(url_content, 'html.parser')
                # list_videos_subsection = get_url_videos_site(subsection_bs)
                # list_url_videos_site = list_url_videos_site + list(get_url_videos_site(subsection_bs))
        # else:
            # list_url_videos_site = get_url_videos_site(job_section_element)

        # for video_site in list_url_videos_site:

            # for content_site_element in get_content_video_site(video_site):
                # video_name = get_video_name_from_site(content_site_element)
                # video_url = get_video_url_from_site(content_site_element)
                # video_genre = get_video_genre_from_site(content_site_element)
                # video_description = get_video_description_from_site(content_site_element)
                # video_thumb = get_video_thumb_from_site(content_site_element)

                # video_group_element = dict()
                # video_group_element['name'] = video_name
                # video_group_element['thumb'] = video_thumb
                # video_group_element['video'] = video_url
                # video_group_element['genre'] = video_genre
                # video_group_element['description'] = video_description

                # # yield video_group_element
                # retour_videos.append(video_group_element)

        # save_dict(retour_videos, chemin_fichier_videos)
    return retour_videos


def convert_video_path(path_video):
    """
    Convert path string to exact path string
    considering video type (Vimeo, Youtube, other).
    """

    return_path = ''

    # Chargement de la page des vidéos...
    url_content = urlopen(path_video).read()
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
    retour_bool = False
    if not os.path.isfile(fichier):
        retour_bool = True
    else:
        criticalTime = arrow.now().shift(hours=+5).shift(days=-jours)
        # if os.stat(f).st_mtime < now - 7 * 86400:
        itemTime = arrow.get(os.stat(fichier).st_mtime)
        if itemTime < criticalTime:
            retour_bool = True
    return retour_bool

def save_dict(data_dict, fichier):
    """
    Save data structure dict in a file.
    """
    retour_reussite = True
    try:
        file = open(fichier, 'w')
    except IOError:
        retour_reussite = False
        return retour_reussite
    finally:
        file.write(json.dumps(data_dict, indent=4))
        file.close()
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
        # url_content= urllib.request.urlopen(href_element['href']).read()
        url_content= urlopen(href_element['href']).read()
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

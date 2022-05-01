# -*- coding: utf-8 -*-
# Free videos are provided by nfb.ca

# from urllib.parse import urlparse
from urllib.parse import quote
from urllib.request import Request, urlopen

import os.path

# Import libraries to analyse Web pages
from bs4 import BeautifulSoup

import os

import json
import hashlib

import re

import datetime

import random

ADDON_ID = 'plugin.video.onf'

URL_PREFIXE = 'https://onf.ca'
URL_ADRESSE_PRINCIPALE = URL_PREFIXE + '/index.php'

URL_ADRESSE_FILMS = URL_PREFIXE + '/films'
URL_ADRESSE_FILM = URL_PREFIXE + '/film'

URL_ADRESSE_SERIES = URL_PREFIXE + '/series'

URL_ADRESSE_CHAINES = URL_PREFIXE + '/chaines'

URLS_ADRESSES = [ URL_ADRESSE_SERIES, URL_ADRESSE_CHAINES, URL_ADRESSE_FILMS, URL_ADRESSE_PRINCIPALE ]

NOMBRE_CHARGEMENT_WEB = 0

FICHIER_CATEGORIES = 'get_categories.json'
FICHIER_VIDEOS = 'get_videos_'  # On ajoutera sha1 et .json
FICHIER_VIDEOS_DOMAINS = 'list_url_domains.json'

# Nombre de jours maximum pour le chargement
NOMBRE_JOURS_DELAI_CATEGORIES = 15
NOMBRE_JOURS_DELAI_VIDEOS = 11

# Les pages contenant certains mots ne peuvent être considérés...
URL_A_ENLEVER = ['interactif']

# Section des fils RSS
RSS_TEXTE = 'Ajouts récents (RSS)'

# Variable disponible tout au long de l'exécution du script
CATEGORIES_WITH_URL = []

NB_PAGES_RECHERCHE = 4

def strip_all(chaine):
    """
    Remove non-visible char beginning and end of string.
    Remove carriage return also.
    Remove spaces char beginning and end of string.
    """
    if chaine:
        return chaine.replace('\t', '').replace('\n', '').replace('\r', '').strip(' ')
    else:
        return chaine


def get_random_day(max_days):
    "Calcul le nombre de jours maximum au hasard"
    return random.randint(1, max_days)

def verify_url_prefixe(chaine_url, prefixe_url):
    "Ajouter domaine http au début si non présent"
    if chaine_url[0:4] != 'http':
        return prefixe_url + chaine_url
    else:
        return chaine_url

def verify_url_video_inside(url):
    "Vérifier s'il y a au moins une vidéo sur une page"

    reponse_video = False

    url_content= read_url(url)
    liste_soup = BeautifulSoup(url_content, 'html.parser')

    job_a_element = liste_soup.find("a", class_="containerScreenshot")
    if job_a_element and job_a_element.has_attr('href'):
        url_href = job_a_element['href']
        for mot_enleve in URL_A_ENLEVER:
            if url_href and url_href.find(mot_enleve) < 0:
                    reponse_video = True

    return reponse_video

def read_url(url_text):
    "Chargement d'une page Web de façon sécuritaire"
    req = Request(url_text, headers={'User-Agent': 'Mozilla/5.0'})

    try:
        url_content = urlopen(req).read()
    except:
        url_content = None

    return url_content

# def parseurl_redirect(url_text):
    # req = Request(url_text, headers={'User-Agent': 'Mozilla/5.0'})

    # return_url = url_text
    # try:
        # resp = urlopen(req, timeout=6)
    # except:
        # resp= None
    # if resp:
        # if resp.geturl() != url_text:
            # return_url = resp.geturl()

    # return resp.geturl()

def url_exclure(text):
    "Vérifier si des mots à exclure sont présents"

    reponse = False

    for chaine in URL_A_ENLEVER:
        if chaine in text:
            reponse = True

    return reponse


def add_h2h3_category(content_bs, categories_url):
    "Cherche une categorie h2 avec classe h3 et retourne la nouvelle liste"

    retour_categories_url = categories_url
    job_h2_elements = content_bs.find_all("h2", class_="h3")
    for job_h2_element in job_h2_elements:
        if job_h2_element.text and (not job_h2_element.text in [category_tuple[0] for category_tuple in retour_categories_url]):
            job_href_element = job_h2_element.find("a")
            if job_href_element and job_href_element.has_attr('href'):
                url_video = verify_url_prefixe(job_href_element['href'], URL_PREFIXE)
                if not url_exclure(url_video):
                    retour_categories_url.append((strip_all(job_href_element.text), url_video))
    return retour_categories_url

def add_chaine_category(content_bs, categories_url):
    "Cherche une categorie a et retourne la nouvelle liste"

    retour_categories_url = categories_url
    job_a_elements = content_bs.find_all("a")
    for job_a_element in job_a_elements:
        job_span_element = job_a_element.find('span', class_="labelChaine")
        if job_span_element and job_a_element.has_attr('href') and (not job_span_element.text in [category_tuple[0] for category_tuple in retour_categories_url]):
                url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
                if not url_exclure(url_video):
                    retour_categories_url.append((strip_all(job_span_element.text), url_video))
    return retour_categories_url

def add_serie_category(content_bs, categories_url):
    "Cherche une categorie li et retourne la nouvelle série"

    retour_categories_url = categories_url
    job_a_elements = content_bs.find_all('a', class_='titre')
    for job_a_element in job_a_elements:
        if job_a_element.has_attr('href'):
            url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
            if not url_exclure(url_video):
                retour_categories_url.append((strip_all(job_a_element.text), url_video))

    return retour_categories_url

def add_titre_category(content_bs, categories_url):
    "Cherche une categorie a classe titre et retourne la nouvelle liste"

    retour_categories_url = categories_url
    job_a_elements = content_bs.find_all("a", class_="titre")
    for job_a_element in job_a_elements:
        if job_a_element.text and job_a_element.has_attr('href') and (not job_a_element.text in [category_tuple[0] for category_tuple in retour_categories_url]):
            url_video = verify_url_prefixe(job_a_element['href'], URL_PREFIXE)
            if not url_exclure(url_video):
                retour_categories_url.append((strip_all(job_a_element.text), url_video))
    return retour_categories_url

def add_rss_category(content_bs, categories_url):
    "Cherche une categorie rss et retourne la nouvelle liste"

    retour_categories_url = categories_url
    job_rss_element = content_bs.find('link', {'type': "application/rss+xml"})
    if job_rss_element and job_rss_element.has_attr('href'):
        url_rss = verify_url_prefixe(job_rss_element['href'], URL_PREFIXE)
        retour_categories_url.append((RSS_TEXTE, url_rss))
    return retour_categories_url


def get_categories(content_bs=None, cache_ok=True):
    """
    Get the list of video categories.

    Here you can insert some parsing code that retrieves
    the list of video categories (e.g. 'Movies', 'TV-shows', 'Documentaries' etc.)
    from some site or API.

    note:: Consider using `generator functions <https://wiki.python.org/moin/Generators>`_
        instead of returning lists.

    :return: The list of video categories
    :rtype: types.GeneratorType
    """

    # Variable disponible tout au long de l'exécution du script
    global CATEGORIES_WITH_URL

    chemin_fichier_cat = get_addondir() + FICHIER_CATEGORIES

    retour_categories_url = []

    # Sinon, vérifie les fichiers locaux...
    if cache_ok and not check_file_older_than(chemin_fichier_cat, NOMBRE_JOURS_DELAI_CATEGORIES):
        retour_categories_url = load_dict(chemin_fichier_cat)
    else:

        if content_bs:
            retour_categories_url = add_h2h3_category(content_bs, retour_categories_url)

            # Aller chercher le fil RSS
            retour_categories_url = add_rss_category(content_bs, retour_categories_url)

        else:

            for url_ad in URLS_ADRESSES:
                url_content = read_url(url_ad)
                liste_soup = BeautifulSoup(url_content, 'html.parser')

                retour_categories_url = add_h2h3_category(liste_soup, retour_categories_url)

                if url_ad == URL_ADRESSE_CHAINES:
                    retour_categories_url = add_chaine_category(liste_soup, retour_categories_url)

                if url_ad == URL_ADRESSE_SERIES:
                    retour_categories_url = add_serie_category(liste_soup, retour_categories_url)

                if url_ad == URL_ADRESSE_SERIES:
                    retour_categories_url = add_titre_category(liste_soup, retour_categories_url)

                # Aller chercher le fil RSS
                if url_ad == URL_ADRESSE_PRINCIPALE:
                    retour_categories_url = add_rss_category(liste_soup, retour_categories_url)

        # Sauvegarde de la liste des catérogies avec les URL associés.
        save_dict(retour_categories_url, chemin_fichier_cat)

    CATEGORIES_WITH_URL = retour_categories_url
    return [category_tuple[0] for category_tuple in retour_categories_url]

def get_video_name_from_site(content_bs):
    "Extraire le titre de la vidéo"
    return_name = ''
    if content_bs:
        job_h1_element = content_bs.find("h1")
        if job_h1_element:
            return_name = strip_all(job_h1_element.text)

    return return_name

def get_video_url_from_site(content_bs = None, url_text = None):
    "Extraire l'URL de la vidéo"

    if content_bs:
        liste_soup_video = content_bs
    else:
        url_content = read_url(verify_url_prefixe(url_text, URL_PREFIXE))
        liste_soup_video = BeautifulSoup(url_content, 'html.parser')

    return_url = ''
    job_embed_element = liste_soup_video.find('iframe', {'id': "player-iframe"})
    if job_embed_element and job_embed_element.has_attr('src'):
        return_url = verify_url_prefixe(job_embed_element['src'], URL_PREFIXE)

    # Conversion finale de l'URL de la vidéo...
    # return convert_video_path(return_url)
    return return_url

def get_video_genre_from_site(content_bs):
    "Extraire le genre de la vidéo"

    return_genre = ''

    job_shortinfos_element = content_bs.find('div', class_="shortInfos")
    if job_shortinfos_element:
        job_name_element = content_bs.find('span', {'itemprop': 'name'})
        if job_name_element:
            return_genre += 'Réalisation: ' + strip_all(job_name_element.text)

        job_date_element = job_shortinfos_element.find('span', class_="published")
        if job_date_element:
            return_genre += ', Date: ' + strip_all(job_date_element.text)
        job_duree_element = job_shortinfos_element.find('span', class_="duration duree")
        if job_duree_element:
            return_genre += ', Durée: ' + strip_all(job_duree_element.text)

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
    if job_thumb_element and job_thumb_element.has_attr('href'):
    # if job_thumb_element:
        return_thumb = job_thumb_element['href']
    return return_thumb

def append_video(video_element, liste_videos):
    "Ajoute une vidéo dans le dictionnaire sans répétition seulement"

    test_ajout = True

    # Si le champ est vide, on n'ajoute pas...
    if not video_element['video']:
        test_ajout = False

    if test_ajout:
        # On vérifie l'URL est la même...
        for element in liste_videos:
            if element['video'] == video_element['video']:
                test_ajout = False

    if test_ajout:
        liste_videos.append(video_element)

def get_videos(category, cache_ok=True):
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
    url_category = ''

    # Sinon, vérifie les fichiers locaux...
    # On vérifie si le fichier est plus vieux qu'un nombre de jours au hasard entre 1 et NOMBRE_JOURS_DELAI_VIDEOS
    # On vérifie si la catégorie n'est pas le lien RSS.
    # if cache_ok and category != RSS_TEXTE and not check_file_older_than(chemin_fichier_videos, NOMBRE_JOURS_DELAI_VIDEOS, True):
    if cache_ok and not check_file_older_than(chemin_fichier_videos, NOMBRE_JOURS_DELAI_VIDEOS, True):
        retour_videos = load_dict(chemin_fichier_videos)
    else:

        # Vérifier si la variable de la liste des catégories n'est pas vide.
        if not CATEGORIES_WITH_URL:
            # get_categories(liste_soup)
            get_categories()
        if category in dict(CATEGORIES_WITH_URL):
            url_category = (dict(CATEGORIES_WITH_URL))[category]

        # Chargement seulement si l'URL existe...
        if url_category:

            # Chargement de la page des vidéos...
            url_content = read_url(url_category)

            # Vérifier si c'est un fil RSS...
            if category == RSS_TEXTE:
                liste_soup_category = BeautifulSoup(url_content, 'html5lib')

                articles_soupe = liste_soup_category.findAll('item')
                for article in articles_soupe:
                    video_group_element = dict()
                    # On cherche l'URL d'un item du fil RSS...
                    guid_soup = article.find('guid')
                    if guid_soup:
                        article_link = strip_all(guid_soup.text)
                        url_content = read_url(verify_url_prefixe(article_link, URL_PREFIXE))
                        if url_content:
                            liste_soup_video = BeautifulSoup(url_content, 'html.parser')
                            video_group_element['name'] = get_video_name_from_site(liste_soup_video)
                            video_group_element['video'] = get_video_url_from_site(liste_soup_video)
                            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
                            video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
                            video_group_element['description'] = get_video_description_from_site(liste_soup_video)
                            append_video(video_group_element, retour_videos)

            # On vérifie si l'URL est une série...
            elif url_category.find('series'):
                # La page contient des séries dans une liste de vignettes...
                liste_soup_category = BeautifulSoup(url_content, 'html.parser')
                job_li_elements = liste_soup_category.find_all('li', class_='vignette gratuit')
                for job_li_element in job_li_elements:
                    video_group_element = dict()
                    if job_li_element.has_attr('id') and len(job_li_element['id']) >= 5:
                        url_video = URL_ADRESSE_FILM + '/' + job_li_element['id'][5:]
                        url_content = read_url(url_video)
                        print(url_video)
                        if url_content:
                            liste_soup_video = BeautifulSoup(url_content, 'html.parser')
                            video_group_element['name'] = get_video_name_from_site(liste_soup_video)
                            video_group_element['video'] = get_video_url_from_site(liste_soup_video)
                            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
                            video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
                            video_group_element['description'] = get_video_description_from_site(liste_soup_video)
                            append_video(video_group_element, retour_videos)
            else:
                liste_soup_category = BeautifulSoup(url_content, 'html.parser')

                # La page contient plusieurs vidéos...
                job_a_elements = liste_soup_category.find_all("a", class_="containerScreenshot")
                for job_a_element in job_a_elements:
                    video_group_element = dict()

                    # Chargement de la page d'une vidéo...
                    if job_a_element.has_attr('href'):
                        url_href = job_a_element['href']
                        url_content = read_url(verify_url_prefixe(url_href, URL_PREFIXE))
                        if url_content:
                            liste_soup_video = BeautifulSoup(url_content, 'html.parser')
                            video_group_element['name'] = get_video_name_from_site(liste_soup_video)
                            video_group_element['video'] = get_video_url_from_site(liste_soup_video)
                            video_group_element['thumb'] = get_video_thumb_from_site(liste_soup_video)
                            video_group_element['genre'] = get_video_genre_from_site(liste_soup_video)
                            video_group_element['description'] = get_video_description_from_site(liste_soup_video)
                            append_video(video_group_element, retour_videos)


        save_dict(retour_videos, chemin_fichier_videos)

    return retour_videos

def convert_video_path(path_video):
    """
    Convert path string to exact path string
    considering video type (Vimeo, Youtube, other).
    """

    return_path = ''

    # Chargement de la page des vidéos...
    url_content = read_url(path_video)

    if isinstance(url_content, (bytes, bytearray)):
        url_content_str = url_content.decode()
    else:
        url_content_str = url_content

    resultat_search = re.search(r"source\s*:\s*'(.*)'", url_content_str)
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
    #   /home/*user*/.kodi/userdata/addon_data/plugin.video.onf/

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

def verify_exist_config():
    "Vérifier si le fichier de configuration de base existe dans Kodi"

    chemin_fichier_cat = get_addondir() + FICHIER_CATEGORIES

    fichier_exist = False
    try:
        fichier_exist = os.path.isfile(chemin_fichier_cat)

    except IOError:
        pass

    return fichier_exist

def check_file_older_than(fichier, jours_max, hasard_actif=False):
    """
    Verify if file is old than a certain number of days jours_max.
    If file does not exist, the answer is true.
    If hasard_actif, le number of days is between 1 and jours_max
    """

    global NOMBRE_CHARGEMENT_WEB

    fichier_date = fichier + '.date'

    if hasard_actif:
        jours = get_random_day(jours_max)
    else:
        jours = jours_max

    retour_bool = False

    if not (os.path.isfile(fichier) and os.path.isfile(fichier_date)):
        retour_bool = True
    else:
        if (NOMBRE_CHARGEMENT_WEB < 3) or (not hasard_actif):
            criticalTime = datetime.datetime.today() - datetime.timedelta(days=jours)
            try:
                file_date = open(fichier_date, 'r')
            except IOError:
                return retour_bool

            finally:
                content_time = strip_all(file_date.read())
                try:
                    itemTime = datetime.datetime.strptime(content_time, "%Y-%m-%d")
                except TypeError:
                    import time
                    itemTime = datetime.datetime.fromtimestamp(time.mktime(time.strptime(content_time, "%Y-%m-%d")))

                if itemTime < criticalTime:
                    retour_bool = True
                file_date.close()

    if (not retour_bool) and hasard_actif:
        NOMBRE_CHARGEMENT_WEB += 1
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
        file_date.write(datetime.datetime.now().strftime("%Y-%m-%d"))
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

    # https://services.nfb.ca/api/search/v4/films/?q=tes&per_page=10&language=fr&safe_search=false&sort_by=relevance&order_by=desc&include=description&page=1
    NOUV_URL_ADRESSE = 'https://services.nfb.ca/api/search/v4/films/' + '?q=' + quote(keywordsearch) + '&per_page=10&language=fr&safe_search=false&sort_by=relevance&order_by=desc&include=description&page='

    for nombre in range(NB_PAGES_RECHERCHE):
        page = nombre + 1
        url_content= read_url(NOUV_URL_ADRESSE + str(page))
        if url_content:
            try:
                content_json = json.loads(url_content)
            except:
                content_json = '{}'
            if 'meta' in content_json and 'thumbnail_pattern' in content_json['meta']:
                thumb_1 = content_json['meta']['thumbnail_pattern']
                thumb_2 = thumb_1.replace('{width}', '704')
                thumb_3 = thumb_2.replace('{height}', '396')

            if 'items' in content_json and content_json['items']:
                for item in content_json['items']:
                    if 'title' in item and 'thumbnail_path' in item and 'slug' in item and 'description' in item and 'directors' in item and 'time' in item and 'year' in item:
                        video_group_element = dict()
                        video_group_element['name'] = item['title']
                        # video_group_element['thumb'] = 'https://dkyhanv6paotz.cloudfront.net/live/fit-in/704x396/medias/nfb_tube/' + item['thumbnail_path']
                        video_group_element['thumb'] = thumb_3.replace('{path}', item['thumbnail_path'])
                        video_group_element['video'] = get_video_url_from_site(None, 'https://www.onf.ca/film/' + item['slug'])
                        genre_time = 'durée: ' + item['time'].replace('PT', '')
                        video_group_element['genre'] = 'Réalisation: ' + item['directors'][0]['name'] + ', ' + genre_time + ', année: ' + str(item['year']) if item['directors'] else genre_time + ', ' + str(item['year'])
                        video_group_element['description'] = item['description']['fr'] if 'fr' in item['description'] else ''
                        yield video_group_element

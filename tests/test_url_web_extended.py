import url_web_extended

from bs4 import BeautifulSoup

# Pour enlever l'avertissement de gestion d'un fichier HTML en XML...
# Ne fonctionne pas pour les tests...
# Si nécessaire, à ajouter dans le script url_web_extended.
from bs4.builder import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings('ignore', category=XMLParsedAsHTMLWarning)

import unittest

class GetWebTests(unittest.TestCase):

    def test_get_categories_non_vides(self):
        categories_returned = url_web_extended.get_categories()
        for category in categories_returned:
            self.assertGreater(len(category), 0, "La catégogie '" + category + "' est vide...")

    def test_get_categories_40(self):
        categories_returned = url_web_extended.get_categories()
        self.assertGreater(len(categories_returned), 40, "Le nombre de catégories est en nombre de moins de 40...")

    def test_get_videos_last(self):
        videos_returned = url_web_extended.get_videos(url_web_extended.get_categories()[-1]) # Ajouts récents (RSS)
        video_expected = {'name': 'Quand tombe la neige', 'video': 'https://onf.ca/film/quand-tombe-la-neige/embed/player/?player_mode=&embed_mode=0&auto_focus=1&context_type=film', 'thumb': 'https://dkyhanv6paotz.cloudfront.net/medias/nfb_tube/thumbs_large/2022/quand-tombe-la-neige-LG.jpg', 'genre': 'Réalisation: Barrie McLean1961 |                12 min Date: 1961', 'description': "Film de vulgarisation scientifique, Quand tombe la neige explique le processus de formation des cristaux de neige et décrit à l'aide d'exemples concrets les différentes sortes de neige, liées au degré de maturation des cristaux. Il est aussi question du rôle que la neige joue par rapport aux végétaux."}
        self.assertCountEqual(video_expected, videos_returned[0])

    # def test_get_videos_nouvellement_en_ligne(self):
    #     nouvellementenligne = 'Nouvellement en ligne'
    #     my_categories = url_web_extended.get_categories()
    #     if nouvellementenligne in my_categories:
    #         self.assertGreater(len(url_web_extended.get_videos(nouvellementenligne)), 100, "La catégogie '" + nouvellementenligne + "' contient moins de 100 éléments...")
    #     else:
    #         self.fail("La catégorie '" + nouvellementenligne + "' n'existe pas!")

class TagsTests(unittest.TestCase):

    def test_h2h3_category(self):

        url_content = url_web_extended.read_url(url_web_extended.URL_ADRESSE_PRINCIPALE)
        liste_soup = BeautifulSoup(url_content, 'html.parser')
        job_h2_elements = liste_soup.find_all("h2", class_="h3")
        self.assertGreater(len(job_h2_elements), 6, "Le nombre de section h2 est en nombre de moins de 6...")

    def test_serie_category(self):

        url_content = url_web_extended.read_url(url_web_extended.URL_ADRESSE_SERIES)
        liste_soup = BeautifulSoup(url_content, 'html.parser')
        job_a_elements = liste_soup.find_all('a', class_='titre')
        self.assertGreater(len(job_a_elements), 5, "Le nombre de section de classe titre est en nombre de moins de 5...")

    def test_chaine_category(self):

        compteur_chaine = 0
        url_content = url_web_extended.read_url(url_web_extended.URL_ADRESSE_CHAINES)
        liste_soup = BeautifulSoup(url_content, 'html.parser')
        job_a_elements = liste_soup.find_all("a")
        for job_a_element in job_a_elements:
            job_span_element = job_a_element.find('span', class_="labelChaine")
            if job_span_element:
                compteur_chaine += 1
        self.assertGreater(compteur_chaine, 6, "Le nombre de section de classe lableChaine est en nombre de moins de 6...")

    def test_rss(self):

        url_content = url_web_extended.read_url(url_web_extended.URL_ADRESSE_PRINCIPALE)
        liste_soup = BeautifulSoup(url_content, 'html.parser')
        job_rss_element = liste_soup.find('link', {'type': "application/rss+xml"})
        self.assertIsNotNone(job_rss_element, "Pas d'URL RSS dans la page principale.")


class SearchTests(unittest.TestCase):


    def test_list_search_results_movie_keyword(self):

        search_results_returned = url_web_extended.get_list_search_results('Québec')
        # search_results_expected = list()
        # search_results_expected.append({'name': 'Nothing to hide',
                                        # 'thumb': 'https://horscine.org/wp-content/uploads/2020/10/nothingtohide.jpg',
                                        # 'video': 'https://player.vimeo.com/video/193515863?dnt=1&app_id=122963',
                                        # 'genre': 'De Marc Meillassoux et Mihaela Gladovic – documentaire – 86 min – 2016 – CC BY-NC-ND',
                                        # 'description': 'Êtes-vous vraiment sûr de n’avoir “rien à cacher”? Que peuvent savoir Facebook ou Google de vous en seulement 30 jours? Votre orientation sexuelle? Vos heures de lever et de coucher? Votre consommation d’alcool et vos infractions pénales? Votre niveau de richesses et votre solvabilité? Marc Meillassoux et Mihaela Gladovic ont fait l’expérience en hackant l’Iphone et l’IMac d’un jeune artiste n’ayant « rien à cacher » pendant un mois. Un hacker et une analyste ont pour mission de deviner qui est ce jeune homme et s’il n’a véritablement “rien à cacher”. Celui-ci est loin de se douter où l’expérience va le mener…'})

        self.assertGreater(len(list(search_results_returned)), 29, "Le nombre de résultats de la recherche de 'Québec' est en nombre de moins de 30...")


class ConvertTests(unittest.TestCase):

    def test_convert_video_path_onf1(self):
        urlvimeo = url_web_extended.convert_video_path('https://onf.ca/film/rose-les/embed/player/?player_mode=&embed_mode=0&auto_focus=1&context_type=film')

        self.assertEqual(urlvimeo, 'https://dcly21uuqtecw.cloudfront.net/hls/1001062_1001061_DM-13377/1001062_1001061_DM-13377.m3u8')

    def test_convert_video_path_onf2(self):
        urlyoutube = url_web_extended.convert_video_path('https://www.onf.ca/film/apatrides/embed/player/?player_mode=&embed_mode=0&auto_focus=1&context_type=film')

        self.assertEqual(urlyoutube, 'https://dcly21uuqtecw.cloudfront.net/hls/1001195_1021296_DM-13539/1001195_1021296_DM-13539.m3u8')

if __name__ == '__main__':
    unittest.main()


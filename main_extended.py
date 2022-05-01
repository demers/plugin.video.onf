# -*- coding: utf-8 -*-
# Module: main
# Author: Roman V. M. and modified by Francois-N. Demers
# Created on: 28.11.2014
# Modified on: 22.1.2022 by adding use of script.module.routing and config
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Video plugin that is compatible with Kodi 19.x "Matrix" and above
"""

import sys
# from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin
import routing
import xbmc
import xbmcaddon

import url_web

# MESSAGE_CHARGEMENT = "Chargement... (entre 2 et 12 min. max.)"
if url_web.verify_exist_config():
    MESSAGE_CHARGEMENT = "Chargement... (-1 min.)"
else:
    MESSAGE_CHARGEMENT = "Configuration initiale... (+/- 20 min.)"


MESSAGE_ERREUR_VIDEO = "Vidéo non-standard.  Risque d'erreur de lecture..."

# Example log: xbmc.log('YOUTUBE')

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]

plugin = routing.Plugin()

def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)

    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(plugin.handle, True, listitem=play_item)


@plugin.route('/')
def index():
    categories = url_web.get_categories()
    xbmcplugin.setPluginCategory(plugin.handle, 'Vidéos ONF/NFB')
    xbmcplugin.setContent(plugin.handle, 'videos')

    # A réactiver quand la recherche fonctionnera...
    url = plugin.url_for(search)
    xbmcplugin.addDirectoryItem(plugin.handle, url, xbmcgui.ListItem("Recherche"), True)


    __addon__ = xbmcaddon.Addon()
    __addonname__ = __addon__.getAddonInfo('name')
    __icon__ = __addon__.getAddonInfo('icon')
    line_notification = MESSAGE_CHARGEMENT
    time = 10000 #in miliseconds
    # https://kodi.wiki/view/GUI_tutorial
    xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line_notification, time, __icon__))

    category_number = 0
    for category in categories:

        videos = url_web.get_videos(category)
        if url_web.is_iterator(videos):
            video_item = next(videos)
        else:
            if videos:
                video_item = videos[0]
            else:
                continue

        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item = xbmcgui.ListItem(label=category)
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video_item['thumb'],
                          'icon': video_item['thumb'],
                          'fanart': video_item['thumb']})
        # Set additional info for the list item.
        # Here we use a category name for both properties for for simplicity's sake.
        # setInfo allows to set various information for an item.
        # For available properties see the following link:
        # https://codedocs.xyz/xbmc/xbmc/group__python__xbmcgui__listitem.html#ga0b71166869bda87ad744942888fb5f14
        # 'mediatype' is needed for a skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': category,
                                    'genre': category,
                                    'plot': category,
                                    'mediatype': 'video'})
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=listing&category=Animals
        url = plugin.url_for(show_category, category_number)
        # is_folder = True means that this item opens a sub-list of lower level items.
        is_folder = True
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, is_folder)
        category_number += 1

    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(plugin.handle)

# https://forum.kodi.tv/showthread.php?tid=312476
def get_user_input():
    kb = xbmc.Keyboard('', 'Entrez ce que vous cherchez... ')
    kb.doModal() # Onscreen keyboard appears
    if not kb.isConfirmed():
        return
    query = kb.getText() # User input
    return query

# EN COMMENTAIRE POUR CACHER CET OPTION...
@plugin.route('/search')
def search():
    query_result = get_user_input()

    xbmcplugin.setPluginCategory(plugin.handle, 'Résultats de recherche')
    xbmcplugin.setContent(plugin.handle, 'videos')

    list_results = url_web.get_list_search_results(query_result)

    for result_item in list_results:

        # url = plugin.url_for(show_search_result, query)
        # query_result = plugin.args['query'][0]
        list_item = xbmcgui.ListItem(label=result_item['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.

        list_item.setInfo('video', {'title': result_item['name'],
                                    'genre': result_item['genre'],
                                    'plot': result_item['description'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': result_item['thumb'], 'icon': result_item['thumb'], 'fanart': result_item['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        # url = plugin.url_for(show_category, category)
        # url = plugin.url_for(route_play_video, result_item['video'])
        url_for_sent = result_item['video']
        url = plugin.url_for(route_play_video, url_result=url_for_sent)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, is_folder)
        # xbmcplugin.addDirectoryItem(plugin.handle, "", xbmcgui.ListItem("Vous avez cherché pour '%s'" % query_result))

    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/category/<category_number>')
def show_category(category_number):
    # xbmcplugin.addDirectoryItem(plugin.handle, "", xbmcgui.ListItem("Hello category %s!" % category_id))
    # xbmcplugin.endOfDirectory(plugin.handle)

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
    # category_id = list(url_web.get_categories())[int(category_number)]
    category_id = (url_web.get_categories())[int(category_number)]
    xbmcplugin.setPluginCategory(plugin.handle, category_id)
    # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(plugin.handle, 'videos')
    # Get the list of videos in the category.
    videos = url_web.get_videos(category_id)
    # Iterate through videos.
    video_number = 0
    for video in videos:
        # Create a list item with a text label and a thumbnail image.
        list_item = xbmcgui.ListItem(label=video['name'])
        # Set additional info for the list item.
        # 'mediatype' is needed for skin to display info for this ListItem correctly.
        list_item.setInfo('video', {'title': video['name'],
                                    'genre': video['genre'],
                                    'plot': video['description'],
                                    'mediatype': 'video'})
        # Set graphics (thumbnail, fanart, banner, poster, landscape etc.) for the list item.
        # Here we use the same image for all items for simplicity's sake.
        # In a real-life plugin you need to set each image accordingly.
        list_item.setArt({'thumb': video['thumb'], 'icon': video['thumb'], 'fanart': video['thumb']})
        # Set 'IsPlayable' property to 'true'.
        # This is mandatory for playable items!
        list_item.setProperty('IsPlayable', 'true')
        # Create a URL for a plugin recursive call.
        # Example: plugin://plugin.video.example/?action=play&video=http://www.vidsplay.com/wp-content/uploads/2017/04/crab.mp4
        # url = plugin.url_for(show_category, category)
        url = plugin.url_for(route_play_category_video, category_number, video_number)
        # Add the list item to a virtual Kodi folder.
        # is_folder = False means that this item won't open any sub-list.
        is_folder = False
        # Add our item to the Kodi virtual folder listing.
        xbmcplugin.addDirectoryItem(plugin.handle, url, list_item, is_folder)
        video_number += 1
    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    xbmcplugin.addSortMethod(plugin.handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)
    # Finish creating a virtual folder.
    xbmcplugin.endOfDirectory(plugin.handle)

@plugin.route('/video_category/<category_number>/<video_number>')
def route_play_category_video(category_number, video_number):
    categories = url_web.get_categories()
    # From category_number, extract category_id
    if url_web.is_iterator(categories):
        category_identified = next(x for i,x in enumerate(categories) if i==int(category_number))
    else:
        category_identified = categories[int(category_number)]


    videos = url_web.get_videos(category_identified)
    # From video_number, extract video_id
    if url_web.is_iterator(videos):
        video_identified = next(x for i,x in enumerate(videos) if i==int(video_number))
    else:
        video_identified = videos[int(video_number)]

    exact_video_path_to_play = url_web.convert_video_path(video_identified['video'])
    # exact_video_path_to_play = video_identified['video']

    # # If the URL is not changed...
    # if url_web.convert_video_path(video_identified['video']) == video_identified['video']:
        # __addon__ = xbmcaddon.Addon()
        # __addonname__ = __addon__.getAddonInfo('name')
        # __icon__ = __addon__.getAddonInfo('icon')
        # line_notification = MESSAGE_ERREUR_VIDEO
        # time = 5000 #in miliseconds

        # # https://kodi.wiki/view/GUI_tutorial
        # xbmc.executebuiltin('Notification(%s, %s, %d, %s)'%(__addonname__,line_notification, time, __icon__))

    play_video(exact_video_path_to_play)

@plugin.route('/video')
def route_play_video():

    video_url = plugin.args['url_result'][0]
    # Use function convert_video_path to get exact path string.
    exact_video_path_to_play = url_web.convert_video_path(video_url)
    play_video(exact_video_path_to_play)
    # play_video(video_url)

if __name__ == '__main__':
    plugin.run()

# Module: main
# Author: Roman V. M.
# Created on: 28.11.2014
# License: GPL v.3 https://www.gnu.org/copyleft/gpl.html
"""
Example video plugin that is compatible with Kodi 19.x "Matrix" and above
"""
import sys
from urllib.parse import urlencode, parse_qsl
import xbmcgui
import xbmcplugin
from lib.utils import *

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]
# Get the plugin handle as an integer number.
_HANDLE = int(sys.argv[1])



def get_url(**kwargs):
    """
    Create a URL for calling the plugin recursively from the given set of keyword arguments.

    :param kwargs: "argument=value" pairs
    :return: plugin call URL
    :rtype: str
    """
    return '{}?{}'.format(_URL, urlencode(kwargs))




def play_video(path):
    """
    Play a video by the provided path.

    :param path: Fully-qualified video URL
    :type path: str
    """
    
    # Create a playable item with a path to play.
    play_item = xbmcgui.ListItem(path=path)
    play_item.setProperty('IsPlayable', 'true')
    # Pass the item to the Kodi player.
    xbmcplugin.setResolvedUrl(_HANDLE, True, listitem=play_item)

def mainmenu():
    itemlist = list()

    itemlist.append(Item(
        label= 'Play Acestream ID',
        action='play'
    ))

    if get_historial():
        itemlist.append(Item(
            label = 'Historial',
            action = 'historial'
        ))


    return itemlist


def get_historial():
    historial = list()
    settings_path= os.path.join(data_path, "historial.json")
    if os.path.isfile(settings_path):
        try:
            historial = load_json_file(settings_path)
        except Exception:
            logger("Error load_file", "error")

    return historial


def add_historial(contenido):
    historial = get_historial()
    settings_path = os.path.join(data_path, "historial.json")

    trobat = False
    for i in historial:
        if i['infohash'] == contenido['infohash']:
            trobat = True
            break

    if not trobat:
        historial.insert(0, contenido)
        dump_json_file(historial[:10], settings_path)


def run(item):
    itemlist = list()
    itemAction = item.action

    if item.action == "mainmenu":
        itemlist = mainmenu()
    elif item.action == "historial":
        for it in get_historial():
            itemlist.append(Item(label= it.get('title'),
                                 action='play',
                                 infohash=it.get('infohash'),
                                 icon=it.get('icon'),
                                 plot=it.get('plot')))

    elif item.action == "play":
        id = url = infohash = None

        #if item.id:
            #id =item.id
        #elif item.url:
         #   url=item.url
        if item.id:
            id=item.id
        elif item.infohash:
            infohash = item.infohash
        else:
            input = xbmcgui.Dialog().input('Insert Acestream ID', "")
            if re.findall('^(http|magnet)', input, re.I):
                url = input
            else:
                id = input

        host = get_setting("ip_addr")
        port = get_setting("ace_port")

        if infohash:
            url= 'http://' + host + ':' + port + '/pid/'+ infohash +'/stream.mp4'
            play_video(url)
        elif id:
            logger("Play Id %s" %id)

            url= 'http://' + host + ':' + port + '/pid/'+ id + '/stream.mp4'
            play_video(url)
            add_historial({'infohash': id,
                           'title': item.title,
                           'icon':  '',
                           'plot': item.plot})


        #xbmc.executebuiltin('Container.Refresh')


    if itemlist:
        for item in itemlist:
            listitem = xbmcgui.ListItem(item.label or item.title)
            listitem.setInfo('video', {'title': item.label or item.title, 'mediatype': 'video'})
            #listitem.setArt(item.getart())
            listitem.setInfo('video', {'plot': item.plot})

            if item.action == "play":
                listitem.setProperty('IsPlayable', 'true')
                isFolder = False
            else:
                isFolder = True
                
            xbmcplugin.addDirectoryItem(
                handle=int(sys.argv[1]),
                url='%s?%s' % (sys.argv[0], item.tourl()),
                listitem=listitem,
                isFolder= isFolder,
                totalItems=len(itemlist)
            )
        
        xbmcplugin.addSortMethod(handle=int(sys.argv[1]), sortMethod=xbmcplugin.SORT_METHOD_NONE)
        xbmcplugin.endOfDirectory(handle=int(sys.argv[1]), succeeded=True)



if __name__ == '__main__':
    # Call the router function and pass the plugin call parameters to it.
    # We use string slicing to trim the leading '?' from the plugin call paramstring
    #router(sys.argv[2][1:])
    logger("argv %s %s" %(sys.argv[1], sys.argv[2]))
    if sys.argv[2]:
        try:
            item = Item().fromurl(sys.argv[2])
            item.title=item.id
        except:
            failed = True
            argumentos = dict()
            for c in sys.argv[2][1:].split('&'):
                k, v = c.split('=')
                argumentos[k] = urllib_parse.unquote_plus(six.ensure_str(v))

            logger("Llamada externa: %s" %argumentos)
            action = argumentos.get('action', '').lower()

            if action == "play" and argumentos.get('id'):
                item=Item(id=argumentos.get('id'), 
                          action='play',
                          title=argumentos.get('title'),
                          iconimage=argumentos.get('iconimage'),
                          plot=argumentos.get('plot'))

                
      #  logger("Call run item")
      #  run(item)
    else:
        item = Item(action='mainmenu')
    #router(sys.argv[2])
    run(item)

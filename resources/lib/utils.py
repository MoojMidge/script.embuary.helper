#!/usr/bin/python
# coding: utf-8

########################

from __future__ import division

import xbmc
import xbmcaddon
import xbmcgui
import xbmcvfs
import random
import os
import locale

import resources.lib.helper as Helper
import resources.lib.library as Library
from resources.lib.json_map import JSON_MAP
import resources.lib.image as Image
from resources.lib.cinema_mode import CinemaMode
from resources.lib.plugin_content import PluginContent

########################

''' Classes
'''


def blurimg(params):
    Image.ImageBlur(
        prop=params.get('prop', 'output'),
        file=Helper.remove_quotes(params.get('file')),
        radius=params.get('radius', None)
    )


def playcinema(params):
    CinemaMode(
        dbid=params.get('dbid'),
        dbtype=params.get('type')
    )


''' Dialogs
'''


def createcontext(params):
    selectionlist = []
    indexlist = []
    splitby = Helper.remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')

    for i in range(1, 100):
        label = xbmc.getInfoLabel('Window(%s).Property(Context.%d.Label)' % (window, i))

        if label == '':
            break

        elif label != 'none' and label != '-':
            selectionlist.append(label)
            indexlist.append(i)

    if selectionlist:
        index = Helper.DIALOG.contextmenu(selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Context.%d.Builtin)' % (window, indexlist[index]))
            for builtin in value.split(splitby):
                Helper.execute(builtin)
                xbmc.sleep(30)

    for i in range(1, 100):
        if window:
            Helper.execute('ClearProperty(Context.%d.Builtin,%s)' % (i, window))
            Helper.execute('ClearProperty(Context.%d.Label,%s)' % (i, window))
        else:
            Helper.execute('ClearProperty(Context.%d.Builtin)' % i)
            Helper.execute('ClearProperty(Context.%d.Label)' % i)


def createselect(params):
    selectionlist = []
    indexlist = []
    headertxt = Helper.remove_quotes(params.get('header', ''))
    splitby = Helper.Helper.remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')
    usedetails = True if params.get('usedetails') == 'true' else False
    preselect = int(params.get('preselect', -1))

    for i in range(1, 100):
        label = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Label)' % (window, i))
        label2 = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Label2)' % (window, i))
        icon = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Icon)' % (window, i))

        if label == '':
            break

        elif label != 'none' and label != '-':
            li_item = xbmcgui.ListItem(label=label, label2=label2, offscreen=True)
            li_item.setArt({'icon': icon})
            selectionlist.append(li_item)
            indexlist.append(i)

    if selectionlist:
        index = Helper.DIALOG.select(headertxt, selectionlist, preselect=preselect, useDetails=usedetails)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Dialog.%d.Builtin)' % (window, indexlist[index]))
            for builtin in value.split(splitby):
                Helper.execute(builtin)
                xbmc.sleep(30)

    for i in range(1, 100):
        if window:
            Helper.execute('ClearProperty(Dialog.%d.Builtin,%s)' % (i, window))
            Helper.execute('ClearProperty(Dialog.%d.Label,%s)' % (i, window))
            Helper.execute('ClearProperty(Dialog.%d.Label2,%s)' % (i, window))
            Helper.execute('ClearProperty(Dialog.%d.Icon,%s)' % (i, window))
        else:
            Helper.execute('ClearProperty(Dialog.%d.Builtin)' % i)
            Helper.execute('ClearProperty(Dialog.%d.Label)' % i)
            Helper.execute('ClearProperty(Dialog.%d.Label2)' % i)
            Helper.execute('ClearProperty(Dialog.%d.Icon)' % i)


def splitandcreateselect(params):
    headertxt = Helper.Helper.remove_quotes(params.get('header', ''))
    seperator = Helper.Helper.remove_quotes(params.get('seperator', ' / '))
    splitby = Helper.remove_quotes(params.get('splitby', '||'))
    window = params.get('window', '')

    selectionlist = Helper.remove_quotes(params.get('items')).split(seperator)

    if selectionlist:
        index = Helper.DIALOG.select(headertxt, selectionlist)

        if index > -1:
            value = xbmc.getInfoLabel('Window(%s).Property(Dialog.Builtin)' % window)
            value = value.replace('???', selectionlist[index])
            for builtin in value.split(splitby):
                Helper.execute(builtin)
                xbmc.sleep(30)

    if window:
        Helper.execute('ClearProperty(Dialog.Builtin,%s)' % window)
    else:
        Helper.execute('ClearProperty(Dialog.Builtin)')


def dialogok(params):
    headertxt = Helper.remove_quotes(params.get('header', ''))
    bodytxt = Helper.remove_quotes(params.get('message', ''))
    Helper.DIALOG.ok(headertxt, bodytxt)


def dialogyesno(params):
    headertxt = Helper.remove_quotes(params.get('header', ''))
    bodytxt = Helper.remove_quotes(params.get('message', ''))
    yesactions = params.get('yesaction', '').split('|')
    noactions = params.get('noaction', '').split('|')

    if Helper.DIALOG.yesno(headertxt, bodytxt):
        for action in yesactions:
            Helper.execute(action)
    else:
        for action in noactions:
            Helper.execute(action)


def textviewer(params):
    headertxt = Helper.remove_quotes(params.get('header', ''))
    bodytxt = Helper.remove_quotes(params.get('message', ''))
    Helper.DIALOG.textviewer(headertxt, bodytxt)


''' Functions
'''


def restartservice(params):
    Helper.execute('NotifyAll(%s, restart)' % Helper.ADDON_ID)


def calc(params):
    prop = Helper.remove_quotes(params.get('prop', 'CalcResult'))
    formula = Helper.remove_quotes(params.get('do'))
    result = eval(str(formula))
    Helper.winprop(prop, str(result))


def settimer(params):
    actions = Helper.remove_quotes(params.get('do'))
    time = params.get('time', '50')
    delay = params.get('delay')
    busydialog = Helper.get_bool(params.get('busydialog', 'true'))

    if busydialog:
        Helper.execute('ActivateWindow(busydialognocancel)')

    xbmc.sleep(int(time))
    Helper.execute('Dialog.Close(all,true)')

    while Helper.Helper.condition('Window.IsVisible(busydialognocancel)'):
        xbmc.sleep(10)

    for action in actions.split('||'):
        Helper.execute(action)
        if delay:
            xbmc.sleep(int(delay))


def encode(params):
    string = Helper.remove_quotes(params.get('string'))
    prop = params.get('prop', 'EncodedString')

    if not Helper.PYTHON3:
        string = string.decode('utf-8')

    Helper.winprop(prop, Helper.url_quote(string))


def decode(params):
    string = Helper.remove_quotes(params.get('string'))
    prop = params.get('prop', 'DecodedString')
    Helper.winprop(prop, Helper.url_unquote(string))


def getaddonsetting(params):
    addon_id = params.get('addon')
    addon_setting = params.get('setting')
    prop = addon_id + '-' + addon_setting

    try:
        setting = xbmcaddon.Addon(addon_id).getSetting(addon_setting)
        Helper.winprop(prop, str(setting))
    except Exception:
        Helper.winprop(prop, clear=True)


def togglekodisetting(params):
    settingname = params.get('setting', '')
    value = False if Helper.Helper.condition('system.getbool(%s)' % settingname) else True

    Helper.json_call(
        'Settings.SetSettingValue',
        params={'setting': '%s' % settingname, 'value': value}
    )


def getkodisetting(params):
    setting = params.get('setting')
    strip = params.get('strip')

    json_query = Helper.json_call(
        'Settings.GetSettingValue',
        params={'setting': '%s' % setting}
    )

    try:
        result = json_query['result']
        result = result.get('value')

        if strip == 'timeformat':
            strip = ['(12h)', ('(24h)')]
            for value in strip:
                if value in result:
                    result = result[:-6]

        result = str(result)
        if result.startswith('[') and result.endswith(']'):
            result = result[1:-1]

        Helper.winprop(setting, result)

    except Exception:
        Helper.winprop(setting, clear=True)


def setkodisetting(params):
    settingname = params.get('setting', '')
    value = params.get('value', '')

    try:
        value = int(value)
    except Exception:
        if value.lower() == 'true':
            value = True
        elif value.lower() == 'false':
            value = False

    Helper.json_call(
        'Settings.SetSettingValue',
        params={'setting': '%s' % settingname, 'value': value}
    )


def toggleaddons(params):
    addonid = params.get('addonid').split('+')
    enable = Helper.get_bool(params.get('enable'))

    for addon in addonid:

        try:
            Helper.json_call(
                'Addons.SetAddonEnabled',
                params={'addonid': '%s' % addon, 'enabled': enable}
            )
            Helper.log('%s - enable: %s' % (addon, enable))
        except Exception:
            pass


def playsfx(params):
    xbmc.playSFX(Helper.remove_quotes(params.get('path', '')))


def stopsfx(params):
    xbmc.stopSFX()


def imginfo(params):
    prop = Helper.remove_quotes(params.get('prop', 'img'))
    img = Helper.remove_quotes(params.get('img'))
    if img:
        width, height, ar = Image.image_info(img)
        Helper.winprop(prop + '.width', str(width))
        Helper.winprop(prop + '.height', str(height))
        Helper.winprop(prop + '.ar', str(ar))


def playitem(params):
    dbtype = params.get('type', '')
    dbid = params.get('dbid', '')
    resume = params.get('resume', True)
    item = params.get('item', '')
    file = Helper.remove_quotes(item)
    protocol = file.split('://')[0]

    if not dbid and not item:
        dbtype = xbmc.getInfoLabel('Container.ListItem.DBTYPE')

        if dbtype:
            dbid = xbmc.getInfoLabel('Container.ListItem.DBID')

        if not dbid:
            file = xbmc.getInfoLabel('Container.ListItem.Filenameandpath') or xbmc.getInfoLabel('Container.ListItem.Path')
            protocol = file.split('://')[0]

    if dbtype == 'song':
        param = 'songid'

    elif dbtype == 'episode':
        method_details = 'VideoLibrary.GetEpisodeDetails'
        param = 'episodeid'
        key_details = 'episodedetails'

    elif dbtype == 'movie':
        method_details = 'VideoLibrary.GetMovieDetails'
        param = 'movieid'
        key_details = 'moviedetails'

    elif dbtype in ['tvshow', 'season']:
        playfolder(params={'dbid': dbid, 'type': dbtype})
        return

    elif dbtype in ['actor', 'country', 'director', 'genre', 'studio', 'tag', 'set', 'playlist', 'artist']:
        Helper.clear_playlists()
        Helper.execute('Dialog.Close(all,true)')
        Helper.execute('Action(Play)')
        return

    if dbid:
        if dbtype == 'song' or not resume:
            position = 0

        else:
            result = Helper.json_call(
                method_details,
                properties=['resume', 'runtime'],
                params={param: int(dbid)}
            )

            try:
                result = result['result'][key_details]
                position = result['resume'].get('position') / result['resume'].get('total') * 100
                resume_time = result.get('runtime') / 100 * position
                resume_time = Helper.get_seconds_str(resume_time)
            except Exception:
                position = 0
                resume_time = None

            if position > 0 and resume != 'force':
                resume_string = xbmc.getLocalizedString(12022)[:-5] + resume_time
                contextdialog = Helper.DIALOG.contextmenu([resume_string, xbmc.getLocalizedString(12021)])

                if contextdialog == 1:
                    position = 0
                elif contextdialog == -1:
                    return

        Helper.clear_playlists()
        Helper.execute('Dialog.Close(all,true)')

        Helper.json_call(
            'Player.Open',
            item={param: int(dbid)},
            options={'resume': position},
        )

    elif protocol == 'plugin' and not dbtype:
        Helper.execute('Action(select)')

    elif file and (item or protocol in ['pvr', 'plugin', 'library']):
        Helper.clear_playlists()
        Helper.execute('Dialog.Close(all,true)')
        # playmedia() because otherwise resume points get ignored
        Helper.execute('PlayMedia(%s)' % file)

    else:
        playall(params={'id': xbmc.getInfoLabel('System.CurrentControlID'), 'method': 'fromhere', 'limit': 1})


def playfolder(params):
    dbid = int(params.get('dbid'))
    shuffled = Helper.get_bool(params.get('shuffle'))

    if shuffled:
        Helper.winprop('script.shuffle.bool', True)

    if params.get('type') == 'season':
        json_query = Helper.json_call(
            'VideoLibrary.GetSeasonDetails',
            properties=['title', 'season', 'tvshowid'],
            params={'seasonid': dbid}
        )
        try:
            result = json_query['result']['seasondetails']
        except Exception as error:
            Helper.log('Play folder error getting season details: %s' % error)
            return

        json_query = Helper.json_call(
            'VideoLibrary.GetEpisodes',
            properties=['episode'],
            query_filter={'operator': 'is', 'field': 'season', 'value': '%s' % result['season']},
            params={'tvshowid': int(result['tvshowid'])}
        )
    else:
        json_query = Helper.json_call(
            'VideoLibrary.GetEpisodes',
            properties=['episode'],
            params={'tvshowid': dbid}
        )

    try:
        result = json_query['result']['episodes']
    except Exception as error:
        Helper.log('Play folder error getting episodes: %s' % error)
        return

    Helper.clear_playlists()

    Helper.json_call(
        'Playlist.Add',
        item=[{'episodeid': episode['episodeid']} for episode in result],
        params={'playlistid': 1}
    )

    Helper.execute('Dialog.Close(all,true)')

    Helper.json_call(
        'Player.Open',
        item={'playlistid': 1, 'position': 0},
        options={'shuffled': shuffled}
    )


def playall(params):
    container = params.get('id')
    method = params.get('method')
    shuffled = Helper.get_bool(method, 'shuffle')
    limit = int(params.get('limit', 0))

    if shuffled:
        Helper.winprop('script.shuffle.bool', True)

    if method == 'fromhere':
        method = 'Container(%s).ListItemNoWrap' % container
    else:
        method = 'Container(%s).ListItemAbsolute' % container

    items = []
    numitems = xbmc.getInfoLabel('Container(%s).NumItems' % container)
    if numitems:
        numitems = int(numitems)
        if numitems > limit > 0:
            numitems = limit
    if not numitems:
        return

    dialog = xbmcgui.DialogProgressBG()
    dialog.create('Loading items to play...')

    for i in range(numitems):

        if Helper.condition('String.IsEqual(%s(%s).DBType,movie)' % (method, i)):
            media_type = 'movie'
        elif Helper.condition('String.IsEqual(%s(%s).DBType,episode)' % (method, i)):
            media_type = 'episode'
        elif Helper.condition('String.IsEqual(%s(%s).DBType,song)' % (method, i)):
            media_type = 'song'
        else:
            media_type = None

        dbid = xbmc.getInfoLabel('%s(%s).DBID' % (method, i))
        url = xbmc.getInfoLabel('%s(%s).Filenameandpath' % (method, i))
        path = os.path.dirname(url) if url else xbmc.getInfoLabel('%s(%s).Path' % (method, i))

        if media_type and dbid:
            items.extend([{'%sid' % media_type: int(dbid)}])

        elif path and (not url or url.endswith('/') or path == url):
            items.extend([{'directory': path, 'recursive': True, 'media': 'music'},
                          {'directory': path, 'recursive': True, 'media': 'video'}])

        elif url:
            items.extend([{'file': url}])

    Helper.clear_playlists()

    Helper.json_call(
        'Playlist.Add',
        item=items,
        params={'playlistid': 0}
    )

    Helper.json_call(
        'Playlist.Add',
        item=items,
        params={'playlistid': 1}
    )

    num_music = int(
        Helper.json_call(
            'Playlist.GetProperties',
            properties=['size'],
            params={'playlistid': 0}
        )['result']['size']
    )

    num_video = int(
        Helper.json_call(
            'Playlist.GetProperties',
            properties=['size'],
            params={'playlistid': 1}
        )['result']['size']
    )

    playlistid = 0 if params.get('type') == 'music' or num_music > num_video else 1

    if num_music or num_video:
        Helper.execute('Dialog.Close(all,true)')
        Helper.json_call(
            'Player.Open',
            item={'playlistid': playlistid, 'position': 0},
            options={'shuffled': shuffled}
        )
    else:
        dialog.close()
        Helper.execute('Action(play)')


def playrandom(params):
    Helper.clear_playlists()
    container = params.get('id')

    i = random.randint(1, int(xbmc.getInfoLabel('Container(%s).NumItems' % container)))

    if Helper.condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,movie)' % (container, i)):
        media_type = 'movie'
    elif Helper.condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,episode)' % (container, i)):
        media_type = 'episode'
    elif Helper.Helper.condition('String.IsEqual(Container(%s).ListItemAbsolute(%s).DBType,song)' % (container, i)):
        media_type = 'song'
    else:
        media_type = None

    item_dbid = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).DBID' % (container, i))
    url = xbmc.getInfoLabel('Container(%s).ListItemAbsolute(%s).Filenameandpath' % (container, i))

    playitem({'type': media_type, 'dbid': item_dbid, 'item': url, 'resume': False})


def jumptoshow_by_episode(params):
    episode_query = Helper.json_call(
        'VideoLibrary.GetEpisodeDetails',
        properties=['tvshowid'],
        params={'episodeid': int(params.get('dbid'))}
    )
    try:
        tvshow_id = str(episode_query['result']['episodedetails']['tvshowid'])
    except Exception:
        Helper.log('Could not get the TV show ID')
        return

    Helper.go_to_path('videodb://tvshows/titles/%s/' % tvshow_id)


def goto(params):
    Helper.go_to_path(Helper.remove_quotes(params.get('path')), params.get('target'))


def resetposition(params):
    containers = params.get('container').split('||')
    only_inactive_container = Helper.get_bool(params.get('only'), 'inactive')
    current_control = xbmc.getInfoLabel('System.CurrentControlID')

    for item in containers:

        try:
            if current_control == item and only_inactive_container:
                raise Exception

            current_item = int(xbmc.getInfoLabel('Container(%s).CurrentItem' % item))
            if current_item > 1:
                current_item -= 1
                Helper.execute('Control.Move(%s,-%s)' % (item, str(current_item)))

        except Exception:
            pass


def details_by_season(params):
    season_query = Helper.json_call(
        'VideoLibrary.GetSeasonDetails',
        properties=JSON_MAP['season_properties'],
        params={'seasonid': int(params.get('dbid'))}
    )

    try:
        tvshow_id = str(season_query['result']['seasondetails']['tvshowid'])
    except Exception:
        Helper.log('Show details by season: Could not get TV show ID')
        return

    tvshow_query = Helper.json_call(
        'VideoLibrary.GetTVShowDetails',
        properties=JSON_MAP['tvshow_properties'],
        params={'tvshowid': int(tvshow_id)}
    )

    try:
        details = tvshow_query['result']['tvshowdetails']
    except Exception:
        Helper.log('Show details by season: Could not get TV show details')
        return

    episode = details['episode']
    watchedepisodes = details['watchedepisodes']
    unwatchedepisodes = Library.get_unwatched(episode, watchedepisodes)

    Helper.winprop('tvshow.dbid', str(details['tvshowid']))
    Helper.winprop('tvshow.rating', str(round(details['rating'], 1)))
    Helper.winprop('tvshow.seasons', str(details['season']))
    Helper.winprop('tvshow.episodes', str(episode))
    Helper.winprop('tvshow.watchedepisodes', str(watchedepisodes))
    Helper.winprop('tvshow.unwatchedepisodes', str(unwatchedepisodes))


def txtfile(params):
    prop = params.get('prop')
    path = xbmc.translatePath(Helper.remove_quotes(params.get('path')))

    if os.path.isfile(path):
        Helper.log('Reading file %s' % path)
        with open(path) as f:
            text = f.read()

        if prop:
            Helper.winprop(prop, text)
        else:
            Helper.DIALOG.textviewer(Helper.remove_quotes(params.get('header')), text)

    else:
        Helper.log('Cannot find %s' % path)
        Helper.winprop(prop, clear=True)


def fontchange(params):
    font = params.get('font')
    fallback_locales = params.get('locales').split('+')

    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].lower()

        for value in fallback_locales:
            if value == shortlocale:
                setkodisetting({'setting': 'lookandfeel.font', 'value': params.get('font')})
                Helper.DIALOG.notification('%s %s' % (value.upper(), Helper.ADDON.getLocalizedString(32004)), '%s %s' % (Helper.ADDON.getLocalizedString(32005), font))
                Helper.log('Locale %s is not supported by default font. Change to %s.' % (value.upper(), font))
                break

    except Exception:
        Helper.log('Auto font change: No system locale found')


def getinfo(params):
    dbid = params.get('dbid')
    dbtype = params.get('type')
    field = params.get('field')
    value = None

    if dbtype == 'movie':
        method = 'VideoLibrary.GetMovieDetails'
        key = 'movieid'
        key_details = 'moviedetails'

    elif dbtype == 'episode':
        method = 'VideoLibrary.GetEpisodeDetails'
        key = 'episodeid'
        key_details = 'episodedetails'

    elif dbtype == 'tvshow':
        method = 'VideoLibrary.GetTVShowDetails'
        key = 'tvshowid'
        key_details = 'tvshowetails'

    try:
        json_query = Helper.json_call(
            method,
            properties=[field],
            params={key: int(dbid)}
        )

        value = json_query['result'][key_details][field]

    except Exception:
        Helper.log('getinfo: No %s info found for %s(%s)' % (field, dbtype, dbid))

    return value


def setinfo(params):
    dbid = params.get('dbid')
    dbtype = params.get('type')
    value = Helper.remove_quotes(str(params.get('value')))

    try:
        value = int(value)
    except Exception:
        value = eval(value)
        pass

    if dbtype == 'movie':
        method = 'VideoLibrary.SetMovieDetails'
        key = 'movieid'

    elif dbtype == 'episode':
        method = 'VideoLibrary.SetEpisodeDetails'
        key = 'episodeid'

    elif dbtype == 'tvshow':
        method = 'VideoLibrary.SetTVShowDetails'
        key = 'tvshowid'

    Helper.json_call(
        method,
        params={key: int(dbid), params.get('field'): value}
    )


def split(params):
    value = Helper.remove_quotes(params.get('value'))
    prop = params.get('prop')
    separator = Helper.remove_quotes(params.get('separator'))

    if value:
        if separator:
            value = value.split(separator)
        else:
            value = value.splitlines()

        i = 0
        for item in value:
            Helper.winprop('%s.%s' % (prop, i), item)
            i += 1

        for item in range(i, 30):
            Helper.winprop('%s.%s' % (prop, i), clear=True)
            i += 1


def lookforfile(params):
    file = Helper.remove_quotes(params.get('file'))
    prop = params.get('prop', 'FileExists')

    if xbmcvfs.exists(file):
        Helper.winprop('%s.bool' % prop, True)
        Helper.log('File exists: %s' % file)

    else:
        Helper.winprop(prop, clear=True)
        Helper.log('File does not exist: %s' % file)


def getlocale(params):
    try:
        defaultlocale = locale.getdefaultlocale()
        shortlocale = defaultlocale[0][3:].upper()
        Helper.winprop('SystemLocale', shortlocale)

    except Exception:
        Helper.winprop('SystemLocale', clear=True)


def deleteimgcache(params, path=Helper.ADDON_DATA_IMG_PATH, delete=False):
    if not delete:
        if Helper.DIALOG.yesno(Helper.ADDON.getLocalizedString(32003), Helper.ADDON.getLocalizedString(32019)):
            delete = True

    if delete:
        for item in os.listdir(path):
            full_path = os.path.join(path, item)
            if os.path.isfile(full_path):
                os.remove(full_path)
            else:
                deleteimgcache(params, full_path, True)


def selecttags(params):
    tags = Helper.get_library_tags()

    if tags:
        Helper.sync_library_tags(tags)

        try:
            whitelist = Helper.addon_data('tags_whitelist.' + xbmc.getSkinDir() + '.data')
        except Exception:
            whitelist = []

        indexlist = {}
        selectlist = []
        preselectlist = []

        index = 0
        for item in sorted(tags):
            selectlist.append(item)
            indexlist[index] = item
            if item in whitelist:
                preselectlist.append(index)
            index += 1

        selectdialog = Helper.DIALOG.multiselect(Helper.ADDON.getLocalizedString(32026), selectlist, preselect=preselectlist)

        if selectdialog is not None and not selectdialog:
            Helper.set_library_tags(tags, [], clear=True)

        elif selectdialog is not None:
            whitelist_new = []
            for item in selectdialog:
                whitelist_new.append(indexlist[item])

            if whitelist != whitelist_new:
                Helper.set_library_tags(tags, whitelist_new)

    elif params.get('silent') != 'true':
        Helper.DIALOG.ok(Helper.ADDON.getLocalizedString(32000), Helper.ADDON.getLocalizedString(32024))


def whitelisttags(params):
    Helper.sync_library_tags(recreate=True)


def refreshinfodialog(params):
    ldbid = xbmc.getInfoLabel('ListItem.DBID')
    ldbtype = xbmc.getInfoLabel('ListItem.DBType')
    force = params.get('force')

    if not ldbid or not ldbtype:
        return

    addon = Helper.get_addon('context.item.extras')
    if addon:
        extras_path = '%s../%s/' if ldbtype == 'episode' else '%s%s/'
        extras_path = extras_path % (xbmc.getInfoLabel('ListItem.Path'), addon.getSetting('extras-folder'))
        lookforfile(params={'file': extras_path, 'prop': 'HasExtras'})

    if force:
        plugin = PluginContent({'dbid': ldbid, 'type': ldbtype, 'infoOnly': True}, list())
        plugin.getbydbid()
        monitor = xbmc.Monitor()
        while not plugin.li:
            monitor.waitForAbort(1)
        Helper.DIALOG.info(plugin.li[0][1])

    resetposition(params={'container': '200||201||202||203||204||205'})
    Helper.execute('SetFocus(100)')


def toggleplaycount(params):
    dbid = params.get('dbid')
    dbtype = params.get('type')

    playcount = getinfo(params={'dbid': dbid, 'type': dbtype, 'field': 'playcount'})
    playcount = 0 if playcount else 1
    setinfo(params={'dbid': dbid, 'type': dbtype, 'field': 'playcount', 'value': playcount})
    monitor = xbmc.Monitor()
    while playcount != getinfo(params={'dbid': dbid, 'type': dbtype, 'field': 'playcount'}):
        monitor.waitForAbort(1)
    if params.get('info'):
        refreshinfodialog(params={'force': True})

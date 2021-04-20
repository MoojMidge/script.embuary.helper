#!/usr/bin/python
# coding: utf-8

########################

import xbmc
import xbmcgui
import random
import os
import time

from resources.lib.utils import split
from resources.lib.helper import *
from resources.lib.image import *
from resources.lib.player_monitor import PlayerMonitor

########################

NOTIFICATION_METHOD = ['VideoLibrary.OnUpdate',
                       'VideoLibrary.OnScanFinished',
                       'VideoLibrary.OnCleanFinished',
                       'AudioLibrary.OnUpdate',
                       'AudioLibrary.OnScanFinished'
                       ]

########################

class Service(xbmc.Monitor):
    def __init__(self):
        self.player_monitor = False
        self.restart = False
        self.screensaver = False
        self.service_enabled = ADDON.getSettingBool('service')

        if self.service_enabled:
            self.start()
        else:
            self.keep_alive()

    def onNotification(self,sender,method,data):
        if ADDON_ID in sender and 'restart' in method:
            self.restart = True

        if method in NOTIFICATION_METHOD:
            sync_library_tags()

            if method.endswith('Finished'):
                reload_widgets(instant=True, reason=method)
            else:
                reload_widgets(reason=method)

    def onSettingsChanged(self):
        log('Service: Addon setting changed', force=True)
        self.restart = True

    def onScreensaverActivated(self):
        self.screensaver = True

    def onScreensaverDeactivated(self):
        self.screensaver = False

    def stop(self):
        if self.service_enabled:
            del self.player_monitor
            log('Service: Player monitor stopped', force=True)
            log('Service: Stopped', force=True)

        if self.restart:
            log('Service: Applying changes', force=True)
            xbmc.sleep(500) # Give Kodi time to set possible changed skin settings. Just to be sure to bypass race conditions on slower systems.
            DIALOG.notification(ADDON_ID, ADDON.getLocalizedString(32006))
            self.__init__()

    def keep_alive(self):
        log('Service: Disabled', force=True)

        while not self.abortRequested() and not self.restart:
            self.waitForAbort(5)

        self.stop()

    def start(self):
        log('Service: Started', force=True)

        self.player_monitor = PlayerMonitor()

        service_interval = xbmc.getInfoLabel('Skin.String(ServiceInterval)') or ADDON.getSetting('service_interval')
        service_interval = float(service_interval)

        background_refresh_interval = xbmc.getInfoLabel('Skin.String(BackgroundInterval)') or ADDON.getSetting('background_interval')
        background_refresh_interval = int(background_refresh_interval)
        background_refresh_elapsed_time = background_refresh_interval

        widget_refresh_interval = 600
        widget_refresh_elapsed_time = 0

        background_grab_interval = 20 * background_refresh_interval
        background_grab_elapsed_time = background_grab_interval

        while not self.abortRequested() and not self.restart:

            ''' Only run timed tasks if screensaver is inactive to avoid keeping NAS/servers awake
            '''
            if self.screensaver:
                self.waitForAbort(service_interval)
                background_grab_elapsed_time += service_interval
                background_refresh_elapsed_time += service_interval
                widget_refresh_elapsed_time += service_interval
                continue
                
            ''' Grab fanarts
            '''
            if background_grab_elapsed_time >= background_grab_interval:
                log('Start new fanart grabber process')
                arts = self.grabfanart()
                background_grab_elapsed_time = 0
                background_refresh_elapsed_time = background_refresh_interval

            ''' Set background properties
            '''
            if background_refresh_elapsed_time >= background_refresh_interval:
                if arts.get('all'):
                    self.setfanart('EmbuaryBackground', arts['all'])
                if arts.get('videos'):
                    self.setfanart('EmbuaryBackgroundVideos', arts['videos'])
                if arts.get('music'):
                    self.setfanart('EmbuaryBackgroundMusic', arts['music'])
                if arts.get('movies'):
                    self.setfanart('EmbuaryBackgroundMovies', arts['movies'])
                if arts.get('tvshows'):
                    self.setfanart('EmbuaryBackgroundTVShows', arts['tvshows'])
                if arts.get('musicvideos'):
                    self.setfanart('EmbuaryBackgroundMusicVideos', arts['musicvideos'])
                if arts.get('artists'):
                    self.setfanart('EmbuaryBackgroundMusic', arts['artists'])

                background_refresh_elapsed_time = 0

            ''' Blur backgrounds
            '''
            if condition('Skin.HasSetting(BlurEnabled)'):
                radius = xbmc.getInfoLabel('Skin.String(BlurRadius)') or ADDON.getSetting('blur_radius')
                ImageBlur(radius=radius)

            ''' Refresh widgets
            '''
            if widget_refresh_elapsed_time >= widget_refresh_interval:
                reload_widgets(instant=True)
                widget_refresh_elapsed_time = 0

            self.waitForAbort(service_interval)
            background_grab_elapsed_time += service_interval
            background_refresh_elapsed_time += service_interval
            widget_refresh_elapsed_time += service_interval

        self.stop()

    def grabfanart(self):
        arts = {}
        arts['movies'] = []
        arts['tvshows'] = []
        arts['musicvideos'] = []
        arts['artists'] = []
        arts['all'] = []
        arts['videos'] = []

        for item in ['movies', 'tvshows', 'artists', 'musicvideos']:
            dbtype = 'Video' if item != 'artists' else 'Audio'
            query = json_call('%sLibrary.Get%s' % (dbtype, item),
                              properties = ['art','file'] if item != 'artists' else ['art'],
                              sort={'method': 'random'}, limit=40
                              )

            try:
                for result in query['result'][item]:
                    if result['art'].get('fanart'):
                        data = {'title': result.get('label', ''), 'path': ''}
                        if result['file']:
                            data.update({'path': 'dbid=%s&amp;type=%s' % (result[item[:-1]+'id'], item[:-1])})
                        data.update(result['art'])
                        arts[item].append(data)

            except KeyError:
                pass

        arts['videos'] = arts['movies'] + arts['tvshows']

        for cat in arts:
            if arts[cat]:
                arts['all'] = arts['all'] + arts[cat]

        return arts

    def setfanart(self,key,items):
        arts = random.choice(items)
        winprop(key, arts.get('fanart', ''))
        for item in ['clearlogo', 'landscape', 'banner', 'poster', 'discart', 'title', 'path']:
            winprop('%s.%s' % (key, item), arts.get(item, ''))
# -*- coding: utf-8 -*-

import os
import sys
import xbmc
import xbmcaddon

# Addon info
__addon__        = xbmcaddon.Addon(id='script.maraschino')
__addonpath__    = __addon__.getAddonInfo('path')
__addonprofile__ = xbmc.translatePath( __addon__.getAddonInfo('profile') ).decode('utf-8')
__setting__      = __addon__.getSetting


# Include paths
sys.path.insert(0, __addonpath__)
sys.path.insert(0, os.path.join(__addonpath__, 'lib'))


def import_modules():
    """All modules that are available in Maraschino are at this point imported."""
    import modules.applications
    import modules.controls
    import modules.couchpotato
    import modules.currently_playing
    import modules.diskspace
    import modules.headphones
    import modules.index
    import modules.library
    import modules.log
    import modules.nzbget
    import modules.recently_added
    import modules.remote
    import modules.sabnzbd
    import modules.script_launcher
    import modules.search
    import modules.sickbeard
    import modules.trakt
    import modules.traktplus
    import modules.transmission
    import modules.updater
    import modules.utorrent
    import modules.weather
    import modules.xbmc_notify
    import mobile


import maraschino

def main():
    maraschino.UPDATER = False
    maraschino.RUNDIR = __addonpath__
    maraschino.DATA_DIR = __addonprofile__
    maraschino.DATABASE = os.path.join(__addonprofile__, 'maraschino.db')
    maraschino.FULL_PATH = os.path.join(__addonpath__, 'Maraschino.py')

    if __setting__('port') and __setting__('port').isdigit():
        maraschino.PORT = int(__setting__('port'))

    if __setting__('hostname'):
        maraschino.HOST = __setting__('hostname')

    if __setting__('webroot'):
        maraschino.WEBROOT = __setting__('webroot')

    print __setting__('kiosk')
    maraschino.KIOSK = __setting__('kiosk') == 'true'

    maraschino.initialize()
    import_modules()
    maraschino.start()

if __name__ == '__main__':
    main()



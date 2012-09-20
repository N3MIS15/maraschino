# -*- coding: utf-8 -*-
"""Ressources to use Maraschino on mobile devices"""

from flask import render_template
from maraschino import app, logger
from maraschino.tools import requires_auth
from modules.recently_added import get_recently_added_episodes
import maraschino

@app.route('/mobile/temp_index_url')
@requires_auth
def mobile_index():
    return render_template('mobile/index.html')

@app.route('/mobile')
@requires_auth
def recently_added_episodes():
    try:
        xbmc = maraschino.XBMC
        recently_added_episodes = xbmc.VideoLibrary.GetRecentlyAddedEpisodes(properties = ['title', 'season', 'episode', 'showtitle', 'playcount', 'thumbnail', 'firstaired'])['episodes']

    except:
        logger.log('Could not retrieve recently added episodes' , 'WARNING')

    return render_template('mobile/recent_episodes.html',
        recently_added_episodes = recently_added_episodes,
        webroot = maraschino.WEBROOT,
    )

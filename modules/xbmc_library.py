from flask import render_template, jsonify, request, json
from maraschino.noneditable import server_api_address
from maraschino.models import Setting
from maraschino.database import db_session
from maraschino.tools import requires_auth, get_setting, get_setting_value
from maraschino import app, logger
import jsonrpclib, random

xbmc_error = 'There was a problem connecting to the XBMC server'
back_id = {
    'movies': None,
    'tvshows': None,
    'seasons': None,
    'episodes': None,
    'artists': None,
    'albums': None
}

library_settings = {
    'movies': [
        {
            'key': 'xbmc_movies_sort',
            'value': 'label',
            'description': 'Sort movies by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'year', 'label': 'Year'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_movies_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_movies_view',
            'value': 'list',
            'description': 'Movies view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
            ]
        },
        {
            'key': 'xbmc_movies_view_sets',
            'value': '0',
            'description': 'Show movie sets',
            'type': 'bool',
        },
        {
            'key': 'xbmc_movies_hide_watched',
            'value': '0',
            'description': 'Hide watched movies',
            'type': 'bool',
        },
    ],
    'tvshows': [
        {
            'key': 'xbmc_tvshows_sort',
            'value': 'label',
            'description': 'Sort TV shows by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'year', 'label': 'Year'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_tvshows_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_tvshows_view',
            'value': 'list',
            'description': 'TV shows view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
                {'value': 'banner', 'label': 'Banner'},
            ]
        },
        {
            'key': 'xbmc_tvshows_hide_watched',
            'value': '0',
            'description': 'Hide watched TV shows',
            'type': 'bool',
        },
    ],
    'seasons': [
        {
            'key': 'xbmc_seasons_view',
            'value': 'list',
            'description': 'Seasons view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'poster', 'label': 'Poster'},
                {'value': 'banner', 'label': 'Banner'},
            ]
        },
        {
            'key': 'xbmc_seasons_hide_watched',
            'value': '0',
            'description': 'Hide watched seasons',
            'type': 'bool',
        },
    ],
    'episodes': [
        {
            'key': 'xbmc_episodes_sort',
            'value': 'label',
            'description': 'Sort episodes by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'year', 'label': 'Year'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_episodes_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_episodes_view',
            'value': 'list',
            'description': 'Episodes view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'thumbnail', 'label': 'Thumbnail'},
            ]
        },
        {
            'key': 'xbmc_episodes_hide_watched',
            'value': '0',
            'description': 'Hide watched episodes',
            'type': 'bool',
        },
    ],
    'artists': [
        {
            'key': 'xbmc_artists_sort',
            'value': 'label',
            'description': 'Sort artists by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_artists_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_artists_view',
            'value': 'list',
            'description': 'Artists view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
            ]
        },
    ],
    'albums': [
        {
            'key': 'xbmc_albums_sort',
            'value': 'label',
            'description': 'Sort albums by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'genre', 'label': 'Genre'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_albums_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
        {
            'key': 'xbmc_albums_view',
            'value': 'list',
            'description': 'Albums view',
            'type': 'select',
            'options': [
                {'value': 'list', 'label': 'List'},
                {'value': 'large_list', 'label': 'Large List'},
                {'value': 'album', 'label': 'Album Cover'},
            ]
        },
    ],

    'songs': [
        {
            'key': 'xbmc_songs_sort',
            'value': 'track',
            'description': 'Sort albums by',
            'type': 'select',
            'options': [
                {'value': 'label', 'label': 'Title'},
                {'value': 'rating', 'label': 'Rating'},
                {'value': 'track', 'label': 'Track'},
                {'value': 'random', 'label': 'Random'},
            ]
        },
        {
            'key': 'xbmc_albums_sort_order',
            'value': 'ascending',
            'description': 'Sort direction',
            'type': 'select',
            'options': [
                {'value': 'ascending', 'label': 'Ascending'},
                {'value': 'descending', 'label': 'Descending'},
            ]
        },
    ],
}

def init_xbmc_media_settings():
    '''
    If library settings are not in
    database, add them with default value.
    '''
    for setting in library_settings:
        for s in library_settings[setting]:
            if get_setting(s['key']) == None:
                new_setting = Setting(key=s['key'], value=s['value'])
                db_session.add(new_setting)
    db_session.commit()

    return

init_xbmc_media_settings()

def get_xbmc_media_settings(media_type):
    '''
    Return settings for media type.
    '''
    if media_type == 'moviesets':
        media_type = 'movies'

    settings = library_settings[media_type]

    for s in settings:
        s['value'] = get_setting_value(s['key'])

    return settings

@app.route('/xhr/xbmc_library/save/<media_type>/', methods=['POST'])
@requires_auth
def save_xbmc_settings(media_type):
    """Save options in settings dialog"""
    try:
        settings = json.loads(request.form['settings'])

        for s in settings:
            setting = get_setting(s['name'])

            setting.value = s['value']
            db_session.add(setting)

        db_session.commit()
    except:
        return jsonify(error=True)

    return jsonify(success=True)


def render_xbmc_library(template='xbmc_library.html',
                        library=None,
                        message=None,
                        settings=None,
                        view='list',
                        media=None,
                        file=None,
                        back_pos=None):
    return render_template(
        template,
        library=library,
        message=message,
        settings=settings,
        view=view,
        media=media,
        file=file,
        back_pos=back_pos,
        show_info=get_setting_value('xbmc_library_show_info') == '1'
    )


def xbmc_sort(media_type):
    '''
    Return sort values for media type.
    '''
    sort = {}
    sort['method'] = get_setting_value('xbmc_'+media_type+'_sort')
    sort['ignorearticle'] = get_setting_value('xbmc_library_ignore_the') == '1'
    sort['order'] = get_setting_value('xbmc_'+media_type+'_sort_order')

    return sort


@app.route('/xhr/xbmc_library/')
@app.route('/xhr/xbmc_library/<media_type>')
@requires_auth
def xhr_xbmc_library_media(media_type=None):
    global back_id
    back_pos = None

    if not server_api_address():
        logger.log('LIBRARY :: No XBMC server defined', 'ERROR')
        return render_xbmc_library(message="You need to configure XBMC server settings first.")

    try:
        if not media_type:
            for item in back_id:
                back_id[item] = None

            return render_xbmc_library()

        xbmc = jsonrpclib.Server(server_api_address())

        if media_type == 'movies':
            library = xbmc_get_movies(xbmc)
            file_type = 'video'

        elif media_type == 'moviesets':
            setid = int(request.args['setid'])
            library = xbmc_get_moviesets(xbmc, setid)
            file_type = 'video'
            back_id['movies'] = request.args['setid']

        elif media_type == 'tvshows':
            library = xbmc_get_tvshows(xbmc)
            file_type = 'video'

        elif media_type == 'seasons':
            tvshowid = int(request.args['tvshowid'])
            library = xbmc_get_seasons(xbmc, tvshowid)
            file_type = 'video'
            back_id['tvshows'] = request.args['tvshowid']

        elif media_type == 'episodes':
            tvshowid = int(request.args['tvshowid'])
            season = int(request.args['season'])
            library = xbmc_get_episodes(xbmc, tvshowid, season)
            file_type = 'video'
            back_id['tvshows'] = request.args['tvshowid']
            back_id['seasons'] = request.args['season']

        elif media_type == 'artists':
            library = xbmc_get_artists(xbmc)
            file_type = 'audio'

        elif media_type == 'albums':
            artistid = int(request.args['artistid'])
            library = xbmc_get_albums(xbmc, artistid)
            file_type = 'audio'
            back_id['artists'] = request.args['artistid']

        elif media_type == 'songs':
            artistid = int(request.args['artistid'])
            albumid = int(request.args['albumid'])
            library = xbmc_get_songs(xbmc, artistid, albumid)
            file_type = 'audio'
            back_id['artists'] = request.args['artistid']
            back_id['albums'] = request.args['albumid']

        template = 'xbmc_library/%s.html' % media_type
        settings = get_xbmc_media_settings(media_type)
        if media_type == 'moviesets':
            view = get_setting_value('xbmc_movies_view')
        else:
            view = get_setting_value('xbmc_%s_view' % media_type)

        if media_type in back_id:
            back_pos = back_id[media_type]

    except Exception as e:
        logger.log('XBMC LIBRARY :: Problem fetching %s' % media_type, 'ERROR')
        logger.log('EXCEPTION :: %s' % e, 'DEBUG')
        return render_xbmc_library(message=xbmc_error)

    return render_xbmc_library(
        template=template,
        library=library,
        settings=settings,
        view=view,
        media=media_type,
        file=file_type,
        back_pos=back_pos
    )


def xbmc_get_movies(xbmc):
    logger.log('LIBRARY :: Retrieving movies', 'INFO')

    sort = xbmc_sort('movies')
    properties = ['playcount', 'thumbnail', 'year', 'rating', 'set']
    view = get_setting_value('xbmc_movies_view')

    movies = xbmc.VideoLibrary.GetMovies(sort=sort, properties=properties)['movies']

    if get_setting_value('xbmc_movies_view_sets') == '1':
        movies = xbmc_movies_with_sets(xbmc, movies)

    if get_setting_value('xbmc_movies_hide_watched') == '1':
        movies = [x for x in movies if not x['playcount']]

    return movies


def xbmc_movies_with_sets(xbmc, movies):
    sort = xbmc_sort('movies')
    sets = xbmc.VideoLibrary.GetMovieSets(sort=sort, properties=['thumbnail', 'playcount'])['sets']

    #Find movies with sets and copy them into the set
    for i in range(len(movies)):
        if movies[i]['set']:
            for set in sets:
                if not 'movies' in set:
                    set['movies'] = []

                if set['label'] == movies[i]['set']:
                    set['movies'].append(movies[i])

    #Add year and rating properties to set
    for set in sets:
        years = []
        ratings = []
        for movie in set['movies']:
            years.append(movie['year'])
            ratings.append(movie['rating'])

        set['year'] = max(years)
        set['rating'] = float(sum(ratings))/len(ratings)

    #Remove movies in sets from movies list
    movies = [x for x in movies if not x['set']]
    #Add the movie sets to the movie list
    movies.extend(sets)

    #We need to re-sort the movies after adding sets
    if sort['method'] != 'random':
        if sort['order'] == 'ascending':
            movies = sorted(movies, key=lambda k: k[sort['method']])
        else:
            movies = sorted(movies, key=lambda k: k[sort['method']], reverse=True)
    else:
        movies = random.shuffle(movies)

    return movies


def xbmc_get_moviesets(xbmc, setid):
    logger.log('LIBRARY :: Retrieving movie set: %s' % setid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']

    sort = xbmc_sort('movies')
    view = get_setting_value('xbmc_movies_view')
    properties = ['playcount', 'thumbnail', 'year', 'rating', 'set']
    params = {'sort': sort, 'properties': properties}
    #Frodo
    if version > 11:
        params['filter'] = {'setid':setid}

    movies = xbmc.VideoLibrary.GetMovies(**params)['movies']

    if version == 11:
        #UNTESTED
        movies = [x for x in movies if 'setid' in x and x['setid'] == setid]

    if get_setting_value('xbmc_movies_hide_watched') == '1':
        movies = [x for x in movies if not x['playcount']]

    movies[0]['setid'] = setid
    movies[0]['setlabel'] = movies[0]['set']
    return movies

def xbmc_get_tvshows(xbmc):
    logger.log('LIBRARY :: Retrieving TV shows', 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']

    sort = xbmc_sort('tvshows')
    properties = ['playcount', 'thumbnail', 'premiered', 'rating']
    if version > 11:
        properties.append('art')
    view = get_setting_value('xbmc_tvshows_view')

    tvshows = xbmc.VideoLibrary.GetTVShows(sort=sort, properties=properties)['tvshows']

    if get_setting_value('xbmc_tvshows_hide_watched') == '1':
        tvshows = [x for x in tvshows if not x['playcount']]

    return tvshows


def xbmc_get_seasons(xbmc, tvshowid):
    logger.log('LIBRARY :: Retrieving seasons for tvshowid: %s' % tvshowid, 'INFO')

    properties = ['playcount', 'showtitle', 'tvshowid', 'season', 'thumbnail', 'episode']
    view = get_setting_value('xbmc_seasons_view')

    seasons = xbmc.VideoLibrary.GetSeasons(tvshowid=tvshowid, properties=properties)['seasons']

    if get_setting_value('xbmc_seasons_hide_watched') == '1':
        seasons = [x for x in seasons if not x['playcount']]

    for season in seasons:
        episodes = xbmc.VideoLibrary.GetEpisodes(
            tvshowid=tvshowid,
            season=season['season'],
            properties=['playcount']
        )['episodes']
        season['watched'] = len([x for x in episodes if x['playcount']])

    return seasons


def xbmc_get_episodes(xbmc, tvshowid, season):
    logger.log('LIBRARY :: Retrieving episodes for tvshowid: %s season: %s' % (tvshowid, season), 'INFO')

    properties = ['playcount', 'season', 'tvshowid', 'showtitle', 'thumbnail', 'firstaired', 'rating']
    view = get_setting_value('xbmc_episodes_view')
    sort = xbmc_sort('episodes')

    episodes = xbmc.VideoLibrary.GetEpisodes(
        tvshowid=tvshowid,
        season=season,
        sort=sort,
        properties=properties
    )['episodes']

    if get_setting_value('xbmc_episodes_hide_watched') == '1':
        episodes = [x for x in episodes if not x['playcount']]

    return episodes


def xbmc_get_artists(xbmc):
    logger.log('LIBRARY :: Retrieving artists', 'INFO')

    properties = ['thumbnail']
    view = get_setting_value('xbmc_artists_view')
    sort = xbmc_sort('artists')

    artists = xbmc.AudioLibrary.GetArtists(sort=sort, properties=properties)['artists']

    return artists


def xbmc_get_albums(xbmc, artistid):
    logger.log('LIBRARY :: Retrieving albums for artistid: %s' % artistid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']
    params = {}

    view = get_setting_value('xbmc_albums_view')
    params['sort'] = xbmc_sort('albums')
    params['properties'] = ['artist', 'year', 'rating', 'thumbnail']

    if version == 11: #Eden
        params['artistid'] =  artistid

    else: #Frodo
        params['filter'] = {'artistid':artistid}

    albums = xbmc.AudioLibrary.GetAlbums(**params)['albums']

    for album in albums:
        album['artistid'] = artistid

        if version > 11: #Frodo
            album['artist'] = album['artist'][0]

    return albums


def xbmc_get_songs(xbmc, artistid, albumid):
    logger.log('LIBRARY :: Retrieving songs for albumid: %s' % albumid, 'INFO')
    version = xbmc.Application.GetProperties(properties=['version'])['version']['major']
    params = {}

    view = 'list'
    sort = xbmc_sort('songs')
    params['properties'] = ['album', 'track', 'playcount', 'year', 'albumid']

    if version == 11: #Eden
        params['artistid'] = artistid
        params['albumid'] = albumid

    else: #Frodo
        params['filter'] = {
            'albumid': albumid
        }

    songs = xbmc.AudioLibrary.GetSongs(**params)['songs']

    for song in songs:
        song['artistid'] = artistid

    return songs

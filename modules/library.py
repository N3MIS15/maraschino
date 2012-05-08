from flask import Flask, render_template
import jsonrpclib
import urllib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *
import maraschino.logger as logger

vfs_url = '/xhr/vfs_proxy/'
xbmc_error = 'There was a problem connecting to the XBMC server'

def frodo_check():
    xbmc = jsonrpclib.Server(server_api_address())
    xbmc_version = xbmc.Application.GetProperties(properties=['version'])['version']
    frodo = xbmc_version['major'] > 11
    return frodo

@app.route('/xhr/library')
@requires_auth
def xhr_library():
    return render_library()

@app.route('/xhr/library/<item_type>')
@requires_auth
def xhr_library_root(item_type):
    api_address = server_api_address()

    if not api_address:
        logger.log('LIBRARY :: No XBMC server defined', 'ERROR')
        return render_library(message="You need to configure XBMC server settings first.")

    try:
        xbmc = jsonrpclib.Server(api_address)
        library = []
        title = "Movies"

        if item_type == 'movies':
            logger.log('LIBRARY :: Retrieving movies', 'INFO')
            library = xbmc.VideoLibrary.GetMovies(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount', 'resume'])

            if get_setting_value('library_watched_movies') == '0':
                logger.log('LIBRARY :: Showing only unwatched movies', 'INFO')
                unwatched = []

                for movies in library['movies']:
                    movie_playcount = movies['playcount']

                    if movie_playcount == 0:
                        unwatched.append(movies)

                unwatched = {'movies': unwatched}
                library = unwatched

        if item_type == 'shows':
            logger.log('LIBRARY :: Retrieving TV shows', 'INFO')
            title = "TV Shows"
            library = xbmc.VideoLibrary.GetTVShows(sort={ 'method': 'label', 'ignorearticle' : True }, properties=['playcount'])

            if get_setting_value('library_watched_tv') == '0':
                logger.log('LIBRARY :: Showing only unwatched TV shows', 'INFO')
                unwatched = []

                for tvshows in library['tvshows']:
                    tvshow_playcount = tvshows['playcount']

                    if tvshow_playcount == 0:
                        unwatched.append(tvshows)

                unwatched = {'tvshows': unwatched}
                library = unwatched

        if item_type == 'artists':
            logger.log('LIBRARY :: Retrieving music', 'INFO')
            title = "Music"
            library = xbmc.AudioLibrary.GetArtists(sort={ 'method': 'label', 'ignorearticle' : True })

            for artist in library['artists']:
                artistid = artist['artistid']
                try:
                    xbmc.AudioLibrary.GetArtistDetails(artistid=artistid, properties=['description', 'thumbnail', 'genre'])
                    artist['details'] = "True"
                except:
                    None


        if item_type == 'files':
            logger.log('LIBRARY :: Retrieving files', 'INFO')
            title = "Files"
            library = {'filemode' : 'true'}
            xbmc.JSONRPC.Ping()

    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>')
@requires_auth
def xhr_library_show(show):
    logger.log('LIBRARY :: Retrieving seasons', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.VideoLibrary.GetSeasons(tvshowid=show, properties=['tvshowid', 'season', 'showtitle', 'playcount'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if get_setting_value('library_watched_tv') == '0':
        logger.log('LIBRARY :: Showing only unwatched seasons', 'INFO')
        unwatched = []

        for seasons in library['seasons']:
            season_playcount = seasons['playcount']

            if season_playcount == 0:
                unwatched.append(seasons)

        unwatched = {'seasons': unwatched}
        library = unwatched

    library['tvshowid'] = show
    title = library['seasons'][0]['showtitle']

    return render_library(library, title)

@app.route('/xhr/library/shows/<int:show>/<int:season>')
@requires_auth
def xhr_library_season(show, season):
    logger.log('LIBRARY :: Retrieving episodes', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = { 'method': 'episode' }

    try:
        library = xbmc.VideoLibrary.GetEpisodes(tvshowid=show, season=season, sort=sort, properties=['tvshowid', 'season', 'showtitle', 'episode', 'plot', 'playcount', 'resume'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if get_setting_value('library_watched_tv') == '0':
        logger.log('LIBRARY :: Showing only unwatched episodes', 'INFO')
        unwatched = []

        for episodes in library['episodes']:
            episode_playcount = episodes['playcount']

            if episode_playcount == 0:
                unwatched.append(episodes)

        unwatched = {'episodes': unwatched}
        library = unwatched

    episode = library['episodes'][0]
    title = '%s - Season %s' % (episode['showtitle'], episode['season'])

    return render_library(library, title)

@app.route('/xhr/library/artists/<int:artist>')
@requires_auth
def xhr_library_artist(artist):
    logger.log('LIBRARY :: Retrieving albums', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = { 'method': 'year' }

    try:
        library = xbmc.AudioLibrary.GetAlbums(artistid=artist, sort=sort, properties=['artistid', 'title', 'artist', 'year'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    library['artistid'] = artist
    title = library['albums'][0]['artist']

    return render_library(library, title)

@app.route('/xhr/library/artists/<int:artist>/<int:album>')
@requires_auth
def xhr_library_album(artist, album):
    logger.log('LIBRARY :: Retrieving songs', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())
    sort = { 'method': 'track' }

    try:
        library = xbmc.AudioLibrary.GetSongs(artistid=artist, albumid=album, sort=sort, properties=['artistid', 'artist', 'album', 'track', 'playcount', 'year'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    song = library['songs'][0]
    title = '%s - %s (%s)' % (song['artist'], song['album'], song['year'])

    return render_library(library, title)

@app.route('/xhr/library/movie/info/<int:movieid>')
@requires_auth
def xhr_library_info_movie(movieid):
    logger.log('LIBRARY :: Retrieving movie details', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties=['title', 'rating', 'year', 'genre', 'plot', 'director', 'thumbnail', 'trailer', 'playcount', 'resume'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    movie = library['moviedetails']
    title = movie['title']
    itemart_url = strip_special(movie['thumbnail'])

    try:
        itemart = vfs_url + itemart_url
    except:
        logger.log('LIBRARY :: No thumbnail found for %s' % movie['title'], 'INFO')
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        movie = movie,
        itemart = itemart,
        frodo = frodo_check()
    )

@app.route('/xhr/library/tvshow/info/<int:tvshowid>')
@requires_auth
def xhr_library_info_show(tvshowid):
    logger.log('LIBRARY :: Retrieving TV show details', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=tvshowid, properties=['title', 'rating', 'year', 'genre', 'plot', 'premiered', 'thumbnail', 'playcount', 'studio'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    show = library['tvshowdetails']
    title = show['title']
    itemart_url = strip_special(show['thumbnail'])

    try:
        itemart = vfs_url + itemart_url
    except:
        logger.log('LIBRARY :: No thumbnail found for %s' % show['title'], 'INFO')
        itemart = None

    bannerart = get_setting_value('library_use_bannerart') == '1'

    return render_template('library.html',
        library = library,
        title = title,
        show = show,
        itemart = itemart,
        bannerart = bannerart,
        frodo = frodo_check()
    )

@app.route('/xhr/library/episode/info/<int:episodeid>')
@requires_auth
def xhr_library_info_episode(episodeid):
    logger.log('LIBRARY :: Retrieving episode details', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=episodeid, properties=['season', 'tvshowid', 'title', 'rating', 'plot', 'thumbnail', 'playcount', 'firstaired', 'resume'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    episode = library['episodedetails']
    title = episode['title']
    itemart_url = strip_special(episode['thumbnail'])

    try:
        itemart = vfs_url + itemart_url
    except:
        logger.log('LIBRARY :: No thumbnail found for %s' % episode['title'], 'INFO')
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        episode = episode,
        itemart = itemart,
        frodo = frodo_check()
    )

@app.route('/xhr/library/artist/info/<int:artistid>')
@requires_auth
def xhr_library_info_artist(artistid):
    logger.log('LIBRARY :: Retrieving artist details', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.AudioLibrary.GetArtistDetails(artistid=artistid, properties=['description', 'thumbnail', 'formed', 'genre'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    artist = library['artistdetails']
    title = artist['label']
    itemart_url = strip_special(artist['thumbnail'])

    try:
        itemart = vfs_url + itemart_url
    except:
        logger.log('LIBRARY :: No thumbnail found for %s' % artist['title'], 'INFO')
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        artist = artist,
        itemart = itemart,
        frodo = frodo_check()
    )

@app.route('/xhr/library/album/info/<int:albumid>')
@requires_auth
def xhr_library_info_album(albumid):
    logger.log('LIBRARY :: Retrieving album details', 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.AudioLibrary.GetAlbumDetails(albumid=albumid, properties=['artistid', 'title', 'artist', 'year', 'genre', 'description', 'albumlabel', 'rating', 'thumbnail'])
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    album = library['albumdetails']
    title = '%s - %s' % (album['artist'], album['title'])
    itemart_url = strip_special(album['thumbnail'])

    try:
        itemart = vfs_url + itemart_url
    except:
        logger.log('LIBRARY :: No thumbnail found for %s' % album['title'], 'INFO')
        itemart = None

    return render_template('library.html',
        library = library,
        title = title,
        album = album,
        itemart = itemart,
        frodo = frodo_check()
    )

@app.route('/xhr/library/files/<file_type>')
@requires_auth
def xhr_library_files_file_type(file_type):
    logger.log('LIBRARY :: Retrieving %s sources' % file_type, 'INFO')
    xbmc = jsonrpclib.Server(server_api_address())

    try:
        library = xbmc.Files.GetSources(media=file_type)
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if file_type == "video":
        title = "Files - Video"
    else:
        title = "Files - Music"

    return render_library(library, title, file_type)

@app.route('/xhr/library/files/<file_type>/dir/', methods=['POST'])
@requires_auth
def xhr_library_files_directory(file_type):
    path = request.form['path']
    path = urllib.unquote(path.encode('ascii')).decode('utf-8')
    logger.log('LIBRARY :: Retrieving %s path: %s' % (file_type, path), 'INFO')

    xbmc = jsonrpclib.Server(server_api_address())
    sort = { 'method': 'file' }

    try:
        library = xbmc.Files.GetDirectory(media=file_type, sort=sort, directory=path)
        sources = xbmc.Files.GetSources(media=file_type)
    except:
        logger.log('LIBRARY :: %s' % xbmc_error, 'ERROR')
        return render_library(message=xbmc_error)

    if path[-7:] == "%2ezip/":
        path = urllib.unquote(path.encode('ascii')).decode('utf-8')
        path = path.replace('zip://', '')

    if "\\" in path:
        windows = True
    else:
        windows = False

    previous_dir = path[0:-1]

    if windows:
        x = previous_dir.rfind("\\")
    else:
        x = previous_dir.rfind("/")

    current_dir = previous_dir[x+1:]
    previous_dir = previous_dir[0:x+1]

    for source in sources['sources']:
        if source['file'] in path:
            current_source = source['file']
            source_label = source['label']

    if not current_source in previous_dir:
        previous_dir = "sources"

    if file_type == "video":
        file_type = "video_directory"
        if not current_source in previous_dir:
            title = "Video - " + source_label
        else:
            title = "Video - " + current_dir
    else:
        file_type = "music_directory"
        if not current_source in previous_dir:
            title = "Music - " + source_label
        else:
            title = "Music - " + current_dir

    if library['files'] == None:
        library['files'] = [{'filetype': 'none'}]

    return render_library(library, title, file_type, previous_dir)

def render_library(library=None, title="Media Library", file_type=None, previous_dir=None, message=None):
    show_info = get_setting_value('library_show_info') == '1'

    return render_template('library.html',
        library = library,
        title = title,
        message = message,
        file_type = file_type,
        previous_dir = previous_dir,
        show_info = show_info,
        library_show_power_buttons = get_setting_value('library_show_power_buttons', '1') == '1',
    )

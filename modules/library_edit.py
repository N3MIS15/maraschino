from flask import Flask, render_template, jsonify
import jsonrpclib

from Maraschino import app
from settings import *
from maraschino.noneditable import *
from maraschino.tools import *

xbmc = jsonrpclib.Server(server_api_address())
vfs_url = '/xhr/vfs_proxy/'

video_genres = [
    'Action',
    'Adventure',
    'Animation',
    'Comedy',
    'Crime',
    'Disaster',
    'Drama',
    'Family',
    'Fantasy',
    'Film Noir',
    'Foreign',
    'History',
    'Holiday',
    'Horror',
    'Indie',
    'Music',
    'Musical',
    'Mystery',
    'Road Movie',
    'Romance',
    'Science Fiction',
    'Sport',
    'Sports Film',
    'Suspense',
    'Thriller',
    'War',
    'Western'
]

audio_genres = [
    'Metal',
    'Rock',
    'Pop'
]

def xbmc_art(url):
    if url == '':
        return None
    else:
        item = vfs_url + strip_special(url)
    return item

#MOVIE
@app.route('/xhr/library/movie/edit/<int:movieid>')
@requires_auth
def xhr_library_edit_movie(movieid):
    properties = [
        'title',
        'sorttitle',
        'rating',
        'studio',
        'tagline',
        'mpaa',
        'set',
        'year',
        'genre',
        'plot',
        'director',
        'thumbnail',
        'fanart',
        'trailer',
        'imdbnumber'
    ]

    movie = xbmc.VideoLibrary.GetMovieDetails(movieid=movieid, properties=properties)['moviedetails']
    itemart = xbmc_art(movie['thumbnail'])
    fanart = xbmc_art(movie['fanart'])

    try:
        sets = xbmc.VideoLibrary.GetMovieSets()['sets']
    except:
        sets = []



    return render_template('library_edit_movie.html',
        movie = movie,
        sets = sets,
        itemart = itemart,
        fanart = fanart,
        genres = video_genres
    )

@app.route('/xhr/library/movie/set/<int:movieid>/', methods=['POST'])
@requires_auth
def xhr_library_set_movie(movieid):
    title = request.form['title']
    sorttitle = request.form['sorttitle']
    plot = request.form['plot']
    genre = request.form['genre'].split(' / ')
    director = request.form['director'].split(' / ')
    year = int(request.form['year'])
    rating = float(request.form['rating'])
    mpaa = request.form['mpaa']
    studio = request.form['studio'].split(' / ')
    tagline = request.form['tagline']
    sets = request.form['set']
    imdbnumber = request.form['imdbnumber']
    trailer = request.form['trailer']

    xbmc.VideoLibrary.SetMovieDetails(
        movieid=movieid,
        title=title,
        sorttitle=sorttitle,
        plot=plot,
        genre=genre,
        director=director,
        year=year,
        rating=rating,
        mpaa=mpaa,
        studio=studio,
        tagline=tagline,
        imdbnumber=imdbnumber,
        trailer=trailer,
    )

    #sets = sets.split(' / ')
    #for set in sets:
    #    xbmc.VideoLibrary.SetMovieDetails(movieid=movieid, set=set)

    return jsonify({ 'status': 'successful'})

#TVSHOW
@app.route('/xhr/library/tvshow/edit/<int:tvshowid>')
@requires_auth
def xhr_library_edit_tvshow(tvshowid):
    properties = [ 
        'title',
        'sorttitle',
        'mpaa',
        'rating',
        'genre',
        'plot',
        'premiered',
        'thumbnail',
        'fanart',
        'studio'
    ]

    show = xbmc.VideoLibrary.GetTVShowDetails(tvshowid=tvshowid, properties=properties)['tvshowdetails']
    itemart = xbmc_art(show['thumbnail'])
    fanart = xbmc_art(show['fanart'])

    return render_template('library_edit_tvshow.html',
        show = show,
        itemart = itemart,
        fanart = fanart,
        genres = video_genres
    )

@app.route('/xhr/library/tvshow/set/<int:tvshowid>/', methods=['POST'])
@requires_auth
def xhr_library_set_tvshow(tvshowid):
    title = request.form['title']
    sorttitle = request.form['sorttitle']
    plot = request.form['plot']
    genre = request.form['genre'].split(' / ')
    premiered = request.form['premiered']
    rating = float(request.form['rating'])
    mpaa = request.form['mpaa']
    studio = request.form['studio']

    xbmc.VideoLibrary.SetTVShowDetails(
        tvshowid=tvshowid,
        title=title,
        sorttitle=sorttitle,
        plot=plot,
        genre=genre,
        premiered=premiered,
        rating=rating,
        mpaa=mpaa,
        studio=studio,
    )

    return jsonify({ 'status': 'successful'})

#EPISODE
@app.route('/xhr/library/episode/edit/<int:episodeid>')
@requires_auth
def xhr_library_edit_episode(episodeid):
    properties = [
        'title',
        'rating',
        'plot',
        'director',
        'writer',
        'season',
        'firstaired',
        'thumbnail',
        'episode',
        'tvshowid',
        'showtitle'
    ]

    episode = xbmc.VideoLibrary.GetEpisodeDetails(episodeid=episodeid, properties=properties)['episodedetails']
    tvshowid = int(episode['tvshowid'])
    season = int(episode['season']) -1
    season = xbmc.VideoLibrary.GetSeasons(tvshowid=tvshowid, properties=['thumbnail'])['seasons'][season]

    itemart = xbmc_art(episode['thumbnail'])
    seasonart = xbmc_art(season['thumbnail'])

    return render_template('library_edit_episode.html',
        episode = episode,
        itemart = itemart,
        seasonart = seasonart,
    )

@app.route('/xhr/library/episode/set/<int:episodeid>/', methods=['POST'])
@requires_auth
def xhr_library_set_episode(episodeid):
    title = request.form['title']
    plot = request.form['plot']
    firstaired = request.form['firstaired']
    rating = float(request.form['rating'])
    director = request.form['director']
    writer = request.form['writer']
    season = int(request.form['season'])
    episode = int(request.form['episode'])

    xbmc.VideoLibrary.SetEpisodeDetails(
        episodeid=episodeid,
        title=title,
        plot=plot,
        director=director,
        writer=writer,
        episode=episode,
        season=season,
        firstaired=firstaired,
        rating=rating
    )

    return jsonify({ 'status': 'successful'})

#ARTIST
@app.route('/xhr/library/artist/edit/<int:artistid>')
@requires_auth
def xhr_library_edit_artist(artistid):
    properties = [
        'description',
        'instrument',
        'style',
        'mood',
        'born',
        'formed',
        'died',
        'disbanded',
        'yearsactive',
        'musicbrainzartistid',
        'genre',
        'thumbnail',
        'fanart'
    ]

    artist = xbmc.AudioLibrary.GetArtistDetails(artistid=artistid, properties=properties)['artistdetails']
    itemart = xbmc_art(artist['thumbnail'])
    fanart = xbmc_art(artist['fanart'])

    return render_template('library_edit_artist.html',
        artist = artist,
        itemart = itemart,
        fanart = fanart,
        genres = audio_genres
    )

@app.route('/xhr/library/artist/set/<int:artistid>/', methods=['POST'])
@requires_auth
def xhr_library_set_artist(artistid):
    description = request.form['description']
    genre = request.form['genre'].split(' / ')
    instrument = request.form['instrument']
    style = request.form['style']
    mood = request.form['mood']
    born = request.form['born']
    formed = request.form['formed']
    died = request.form['died']
    disbanded = request.form['disbanded']
    yearsactive = request.form['yearsactive']
    musicbrainzartistid = request.form['musicbrainzartistid']

    '''
    xbmc.AudioLibrary.SetArtistDetails(
        artistid=artistid,
        description=description,
        instrument=instrument,
        style=style,
        mood=mood,
        born=born,
        formed=formed,
        died=died,
        disbanded=disbanded,
        yearsactive=yearsactive,
        genre=genre,
        musicbrainzartistid=musicbrainzartistid
    )
    '''

    return jsonify({ 'status': 'successful'})

#ALBUM
@app.route('/xhr/library/album/edit/<int:albumid>')
@requires_auth
def xhr_library_edit_album(albumid):
    properties = [
        'title',
        'description',
        'artist',
        'genre',
        'theme',
        'mood',
        'style',
        'type',
        'albumlabel',
        'rating',
        'year',
        'musicbrainzalbumid',
        'musicbrainzalbumartistid',
        'fanart',
        'thumbnail',
        'artistid'
    ]

    album = xbmc.AudioLibrary.GetAlbumDetails(albumid=albumid, properties=properties)['albumdetails']
    itemart = xbmc_art(album['thumbnail'])
    fanart = xbmc_art(album['fanart'])

    return render_template('library_edit_album.html',
        album = album,
        itemart = itemart,
        fanart = fanart,
        genres = audio_genres
    )

@app.route('/xhr/library/album/set/<int:albumid>/', methods=['POST'])
@requires_auth
def xhr_library_set_album(albumid):
    title = request.form['title']
    description = request.form['description']
    artist = request.form['artist']
    genre = request.form['genre'].split(' / ')
    theme = request.form['theme']
    mood = request.form['mood']
    style = request.form['style']
    type = request.form['type']
    albumlabel = request.form['albumlabel']
    rating = float(request.form['rating'])
    year = int(request.form['year'])
    musicbrainzalbumid = request.form['musicbrainzalbumid']

    '''
    xbmc.AudioLibrary.SetAlbumDetails(
        albumid=albumid,
        title=title,
        description=description,
        artist=artist,
        genre=genre,
        theme=theme,
        mood=mood,
        style=style,
        type=type,
        albumlabel=albumlabel,
        rating=rating,
        year=year,
        musicbrainzalbumid=musicbrainzalbumid
    )
    '''

    return jsonify({ 'status': 'successful'})

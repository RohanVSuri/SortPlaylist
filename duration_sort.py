
#script to sort last.fm listening history by duration listened to an album instead of how many plays
#inspired by Daft Punk's Alive 2007 album, in which many songs are 5+ minutes
import pylast 
import config
from pprint import pprint
import time
import sys
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

password_hash = pylast.md5(config.lastfm_password)
network = pylast.LastFMNetwork(api_key=config.lastfm_api_key, api_secret=config.lastfm_api_secret, username=config.lastfm_username, password_hash=password_hash)
user = network.get_user(config.lastfm_username)


scope = "playlist-modify-public"
redirect_uri="http://localhost:8888/callback/"

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id=config.spotify_client_id, 
                                                client_secret=config.spotify_client_secret, 
                                                scope=scope, 
                                                redirect_uri=redirect_uri))


def get_recent_tracks(username):
    # recent_tracks = network.get_user(username).get_recent_tracks(limit=10)
    # pprint(recent_tracks)
    # start = time.time() - 26297
    # end = time.time()
    start = 1632456000
    end = 1633060800
    print(start, end)

    userx = network.get_user(username)
    # recent_tracks = userx.get_recent_tracks(time_from=start, time_to=end, limit=None)
    # recent_tracks = userx.get_recent_tracks(time_from=time.time()-5400, time_to=end, limit=15, cacheable=True)
    recent_tracks = userx.get_recent_tracks(time_from=start, time_to=end, limit=500)
    pprint(recent_tracks)
    return recent_tracks


def get_info(artist, track):
    # have to use spotify search because last.fm is trash and unreliably doesn't have durations/album names for songs
    search = sp.search(q="artist:" + artist + " track:" + track, type="track") 
    info = {"duration" : search['tracks']['items'][0]['duration_ms'],
            "album_title" : search['tracks']['items'][0]['album']['name']}

    return info
    
    

recent = get_recent_tracks(user)
album_list = {}
for i in recent:
    try:
        artist = i[0].get_artist()
        title = i[0].get_title()

        info = get_info(str(artist), str(title))
        album = info['album_title']
        duration = info['duration']
    except Exception as e:
        print(repr(e), "error occured with: ", title)

    print(artist, title, album, duration)
    
    if album in album_list:
        album_list[album] = album_list[album] + duration
    else:
        album_list[album] = duration
    

    
# pprint(album_list)
pprint(sorted(album_list.items(), key=lambda item: item[1], reverse=True))

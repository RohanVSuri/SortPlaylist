import spotipy
import spotipy.util as util
import pylast
import config
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth
from pprint import pprint
from datetime import datetime

scope = "playlist-modify-public"
redirect_uri="http://localhost:8888/callback/"

sp = spotipy.Spotify(auth_manager = SpotifyOAuth(client_id=config.spotify_client_id, 
                                                client_secret=config.spotify_client_secret, 
                                                scope=scope, 
                                                redirect_uri=redirect_uri))
spotify_username = sp.me()['id']
user_id = "spotify:user:" + spotify_username
#creating spotipy object, creating username # user_id
pl_id=input("Paste in the Spotify Playlist URI here(right click playlist, share, copy Spotify URI): ")
#paste in the spotify playlist ID that you want to sort here

password_hash = pylast.md5(config.lastfm_password)
network = pylast.LastFMNetwork(api_key=config.lastfm_api_key, api_secret=config.lastfm_api_secret, username=config.lastfm_username, password_hash=password_hash)
#creating pylast object
user = network.get_user(config.lastfm_username)
#creating user object from pylast object
omitted_songs = []
def create_song_list():
    song_list = []
    offset=0
    while True:
        #has to be in while(True) because playlist_items() only returns 100 songs at a time(why offset variable is used)
        response = sp.playlist_items(pl_id, offset=offset, fields='items.track.name, items.track.artists, items.track.id, items.track.is_local, total' )
        
        if len(response['items']) == 0:
            break

        for i in range(len(response['items'])):
            artist_name = response['items'][i]['track']['artists'][0]['name']
            track_name = response['items'][i]['track']['name']
            track_id = response['items'][i]['track']['id']
            #dissecting response into diff variables

            try:
                playback_date = get_playback_date(artist_name=artist_name, track_name=track_name)
                #gets last time you played the song using function created below
            except IndexError:
                print("The song " + track_name + " by " + artist_name +  " has never been scrobbled OR the name of the song is different in Last.fm and Spotify")
                omitted_songs.append(track_name) 
                #certain songs have different names in Spotify vs. Last.fm, causing nothing to be returned by get_playback_date
                continue 
            except:
                print("Something else went wrong... not sure :(")
                continue

            if response['items'][i]['track']['is_local']: #omits local files, you can't add a local file to a playlist using spotipy
                omitted_songs.append(track_name)
                print("The song " + track_name + " by " + artist_name + "is a local file")
                continue
            else:
                song_list.append(
                    {
                        "track_id" : track_id,
                        "track_name" : track_name,
                        "artist_name" : artist_name,
                        "playback_date" : playback_date
                    }
                    #creating list of dictionaries (one dictionary for each song)
                )
            print(track_name + ", " + artist_name + ", " + track_id + ", " + playback_date)
        offset = offset + len(response['items'])
    return song_list

def sort_list(song_list):
    sorted_list = sorted(song_list, key = lambda date: datetime.strptime(date['playback_date'], '%d %b %Y, %H:%M'))
    return sorted_list
    #sorts list by "DD MMM YYYY, HR:MN" format

def get_playback_date(artist_name, track_name):
    track_scrobbles = user.get_track_scrobbles(artist=artist_name, track=track_name)
    # print(track_scrobbles)
    return track_scrobbles[0].playback_date
    #gets playback date using lastfm

def create_playlist(sorted_list):
    new_playlist = sp.user_playlist_create(spotify_username, "pylast x spotipy sorted by last listened")
    new_playlist_id = "spotify:playlist:" + new_playlist['id']
    #creates new playlist and gets ID
    for i in sorted_list:
        sp.playlist_add_items(new_playlist_id, ["spotify:track:" + i['track_id']])
        #adds every song to playlist
        
l1 = create_song_list()
s_l=sort_list(l1)
create_playlist(s_l)
print("These songs were omitted because Spotify and Last.fm did not match OR were local files: " + str(omitted_songs))
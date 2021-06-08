#!/usr/bin/env python
# coding: utf-8
import os
import spotipy #https://github.com/plamere/spotipy/issues/672
from spotipy.oauth2 import SpotifyOAuth, CacheFileHandler
from dotenv import load_dotenv

def get_device_id():
    devices = sp.devices()['devices']
    for device_type in ['CastAudio', 'Computer']:
        for device in devices:
            if (device['type'] == device_type):
                return device['id']

def get_song_uri(query):
    try:
        search_result = sp.search(q=query, limit=1)['tracks']
        return search_result['items'][0]['uri']
    except:
        return None

def play_song(device_id, songname):
    song_uri = get_song_uri(songname)
    if song_uri is not None:
        sp.start_playback(device_id=device_id, uris=[song_uri])

load_dotenv()
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
USERNAME = os.getenv('USERNAME')

auth_manager = SpotifyOAuth(scope="user-library-read user-read-playback-state app-remote-control user-modify-playback-state",
                            client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI,
                            cache_handler=CacheFileHandler(username=USERNAME))
sp = spotipy.Spotify(auth_manager=auth_manager)

if __name__ == '__main__':
    print(sp.me())
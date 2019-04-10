import requests
from flask import current_app as app


def search_songs(**args):

    url = app.config['CLOUD_MUSIC_API_HOST'] + '/search'
    resp = requests.get(url, params=args)

    if resp.status_code != 200:
        app.logger.error(resp.text)
        return 'Something wrong with the api.', 500

    result = resp.json()['result']
    songs, song_count = result['songs'], result['songCount']

    return {
        'songs': [song_serializer(song) for song in songs],
        'song_count': song_count
    }


def append_song(song_id=None, keywords=None):
    pass

def get_playlist():
    pass



def song_serializer(song:dict):
    return {
        'id': song['id'],
        'name': song['name'],
        'artists': [artist['name'] for artist in song['artists']]
    }
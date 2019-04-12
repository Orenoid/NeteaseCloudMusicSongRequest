import os
import socket
import time

import requests
from flask import current_app as app

from . import create_app, celery

def search_songs(**args):

    search_url = app.config['CLOUD_MUSIC_API_HOST'] + '/search'
    resp = requests.get(search_url, params=args)

    if resp.status_code != 200:
        app.logger.error(resp.text)
        return 'Something wrong with the api.', 500

    result = resp.json()['result']
    songs, song_count = result['songs'], result['songCount']

    return {
        'songs': [song_serializer(song) for song in songs],
        'song_count': song_count
    }

def append_song(song:dict, keywords=None):

    query_url = app.config['CLOUD_MUSIC_API_HOST'] + '/song/url'
    resp = requests.get(query_url, {'id': song['id']})
    song_url = resp.json()['data'][0]['url']
    download_song.delay(song_url, song['name'], song['artist'])

    return {'result': 'success'}


@celery.task
def download_song(url, name, artist):

    app = create_app()
    with app.app_context():
        resp = requests.get(url)
        with open(os.path.join(app.config['MUSIC_PATH'], f'{name}.mp3')) as file:
            file.write(resp.content)


def song_serializer(song:dict):
    return {
        'id': song['id'],
        'name': song['name'],
        'artists': [artist['name'] for artist in song['artists']]
    }

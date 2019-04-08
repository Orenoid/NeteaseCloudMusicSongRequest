import os
import time
from contextlib import contextmanager
from functools import partial
from threading import Lock, Thread

import pygame
from pygame import mixer

mixer.init()
pygame.init()

SONG_END = pygame.USEREVENT + 1
mixer.music.set_endevent(SONG_END)

# TODO playlist 内部换用 Song 对象
# TODO status/playlist/current_idx getter, setter
# TODO Error 简化写法
# TODO 管理playlist和current_idx状态
# TODO 把各类注释、提示信息换回中文。。
# TODO 尝试将StatusConverter封装到Player内部    √


class PlayerError(Exception):
    pass

class StatusError(PlayerError):
    pass


class Song:

    def __init__(self, path, name, file_name=None, artist=None):
        self.path, self.name = path, name
        self.file_name = file_name or os.path.split(path)[1]
        self.artist = artist or 'Unknown'

    def __repr__(self):
        return f'{self.name} - {self.artist}'


class Player:

    state_table = {
        'stop': {'play': 'playing', 'stop': 'stop'},
        'playing': {'pause': 'pause', 'stop': 'stop'},
        'pause': {'unpause': 'playing', 'stop': 'stop'}
    }


    def __new__(cls):
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):

        self._playlist = []
        self._status = 'stop'
        self._current_idx = None

        self.lock = Lock()
        self.stop_lock = Lock()

    @property
    def status(self):
        return self._status

    @property
    def playlist(self):
        return self._playlist

    @property
    def current_idx(self):
        return self._current_idx

    def play(self, index=None):

        with self.switch_status('play') as succeed:
            if not succeed:
                return
            if not hasattr(self, '_song_end_handler'):
                # TODO daemon
                self._song_end_handler = Thread(target=self.song_end_handler)
                self._song_end_handler.start()

            song = self._playlist[self._current_idx]
            mixer.music.load(song)
            mixer.music.play()

    def stop(self):
        with self.stop_lock, self.switch_status('stop') as succeed:
            if not succeed:
                return
            mixer.music.stop()
            if hasattr(self, '_song_end_handler'):
                del self._song_end_handler

    def next_song(self):
        new_index = self._current_idx + 1 \
            if self._current_idx < len(self._playlist) - 1 else 0
        self.switch_song(new_index)

    def previous_song(self):
        new_index = self._current_idx - 1 \
            if self._current_idx > 0 else 0
        self.switch_song(new_index)

    def switch_song(self, index:int):
        # Whatever the current status is, set it to "playing".
        with self.switch_status(status='playing') as succeed:
            if not succeed:
                return
            song = self._playlist[index]
            mixer.music.load(song)
            mixer.music.play()
            self._current_idx = index

    def pause(self):
        with self.switch_status('pause') as succeed:
            if not succeed:
                return
            if not mixer.music.get_busy():
                raise StatusError(f'mixer.music is not busy \
                    while player status is {self._status}.')
            mixer.music.pause()

    def unpause(self):
        with self.switch_status('unpause') as succeed:
            if not succeed:
                return
            if not mixer.music.get_busy():
                raise StatusError(f'mixer.music is not busy \
                    while player status is {self._status}.')
            mixer.music.unpause()

    def append_new_song(self, song:Song, index=None):

        # if not isinstance(song, Song):
        #     raise TypeError('Song instance needed.')
        if index is None:
            self._playlist.append(song)
        else:
            # TODO 1.check playlist length 2.check index type
            self._playlist.insert(index, song)

        if self._current_idx is None:
            self._current_idx = 0

    def append_new_songs_from_folder(self, path='music'):

        path = os.path.abspath(path)
        files = map(partial(os.path.join, path), os.listdir(path))
        files = [file for file in files \
            if os.path.isfile(file) and os.path.splitext(file)[1]=='.mp3']
        self._playlist.extend(files)

        if self._current_idx is None:
            self._current_idx = 0

    @contextmanager
    def switch_status(self, trigger=None, status=None):

        original_status = self._status
        succeed_switching = False

        if trigger is None and status is None:
            raise StatusError('trigger, status至少需要传入一个')
        if status is not None:
            if status not in self.state_table.keys():
                raise StatusError('No such status')
            self._status = status
            succeed_switching = True

        table = self.state_table.get(self._status)
        if table is None:
            raise StatusError(f'播放器状态异常：{self._status}')
        new_status = table.get(trigger)
        if new_status is None:
            print(f'无效操作，当前状态：{self._status}，尝试操作：{trigger}')
        else:
            self._status = new_status
            succeed_switching = True
        try:
            yield succeed_switching
        except Exception as e:
            print(e)
            self._status = original_status

    def song_end_handler(self):

        # 处理一种很极端的情况
        # 原先如果调用stop时出错，状态回滚，而这边刚好判断到状态为stop
        # 线程就会停掉，所以加了个锁，我也不确定有没有必要这么做。。

        while True:
            with self.stop_lock:
                if self._status != 'stop':
                    break
            events = pygame.event.get()
            for event in events:
                if event.type == SONG_END and self._status != 'stop':
                    with self.lock:
                        self.next_song()
            time.sleep(0.2)

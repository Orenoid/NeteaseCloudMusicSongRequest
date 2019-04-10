import socket

from .player import Player

player = Player()

if __name__ == "__main__":
    player.append_new_songs_from_folder()
    player.play()

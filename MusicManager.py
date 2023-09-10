from youtube_dl import YoutubeDL
import mpv

import subprocess
import time
from dataclasses import dataclass
import logging

logger = logging.getLogger("starrylogger")
def log_convertor(loglevel: str, component: str, message: str):
    logger.log(level=logging._nameToLevel[loglevel.upper()], msg=f"{component.stpauserip()}: {message.strip()}")

MPV = mpv.MPV(log_handler=log_convertor, ytdl=True)

@dataclass
class Current:
    title: str = ""
    artist: str = ""
    album: str = ""
    track: str = ""
    duration: int = 0
    cur_time: int = 0
    url: str = ""
    steam_url: str = ""

CURR = Current()

def seconds_to_human(secs: float) -> str:
    t = time.strftime("%M:%S", time.gmtime(secs))
    return t

@dataclass
class MusicManager:
    def __post_init__(self):
        # self.VLCInstance = vlc.Instance()
        # self.VLCPlayer: vlc.MediaPlayer = self.VLCInstance.media_player_new()
        # self.VLCInstance.log_unset()
        self.musicplayer = MPV
        self.musicplayer.fullscreen = False
        self.musicplayer.loop_playlist = 'inf'
        self.musicplayer.force_window = False
        self.musicplayer.idle = True
        self.current_playing = CURR

    def _parse_track_info(self):
        youtube_dl = YoutubeDL()
        y = youtube_dl.extract_info(self.current_playing.url, download=False)
        self.current_playing.title = y["title"]
        self.current_playing.artist = y["artist"]
        self.current_playing.album = y["album"]
        self.current_playing.track = y["track"]

    def _get_stream_url(self, url: str):
        url = subprocess.getoutput(f'youtube-dl -xg -f "bestaudio/best" {url}')
        return url

    def play(self, url: str):
        self.current_playing.url = url
        self.current_playing.steam_url = self._get_stream_url(url)
        self._parse_track_info()
        self.musicplayer.play(self.current_playing.steam_url)
        # Media = self.VLCInstance.media_new(self.current_playing.steam_url)
        # self.VLCPlayer.set_media(Media)
        # self.VLCPlayer.play()

        # while not self.VLCPlayer.is_playing():
        #     ...
        # self.musicplayer.wait_until_playing()
        
        # self.current_playing.duration = self.current_playing.

    def toggle_pause(self):
        self.musicplayer.pause = not self.musicplayer.pause

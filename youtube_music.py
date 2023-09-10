from dataclasses import dataclass
import requests
import ytmusicapi
from ytmusicapi.auth.oauth import YTMusicOAuth
import os
import logging
import webbrowser

@dataclass
class YoutubeMusic:
    configpath: str = ""

    def __post_init__(self):
        self.logger = logging.getLogger("starrylogger")
        
        if not self.configpath:
            self.configpath = os.path.join(
                os.environ.get('APPDATA') or
                os.environ.get('XDG_CONFIG_HOME') or
                os.path.join(os.environ['HOME'], '.config'),
                "starry_config"
            )
        
        if os.path.exists(self.configpath):
            self.yt = ytmusicapi.YTMusic(self.configpath)
        
        self._code = dict()
        self._session = requests.Session()
        self._oauth = YTMusicOAuth(self._session, None)

    def pre_login(self) -> None:
        
        self._code = self._oauth.get_code()
        url = f"{self._code['verification_url']}?user_code={self._code['user_code']}"
        self.logger.info(f"Your Youtube TV login code is {self._code}!")
        self.logger.info(f"If browser didn't open, then go this url ->")
        self.logger.info(f"{url}")

        webbrowser.open(url, new=1)
        self.logger.info("Run [bold blue]`login`[/bold blue] after completing the above flow to complete the login!")

    def login(self) -> None:
        if not self._code:
            self.logger.warning("Run [bold blue]`gencode`[/bold blue] before and then run [bold blue]`login`[/bold blue]!")
            return

        token = self._oauth.get_token_from_code(self._code["device_code"])
        self._oauth.dump_token(token, self.configpath)
        self.yt = ytmusicapi.YTMusic(self.configpath)
        self.logger.info("Successfully logged in!")

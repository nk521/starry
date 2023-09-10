from MusicManager import MusicManager


import logging
from dataclasses import dataclass

class Die(Exception):
    ...

@dataclass
class Parser:
    COMMANDS_LIST = ["volume", "seek", "exit", "play", "pause"]

    def __post_init__(self):
        self.logger = logging.getLogger("starrylogger")
        self.mm = MusicManager()

    def parse(self, command: str) -> None | Die:
        command, *args = command.strip().split(" ")

        if command not in self.COMMANDS_LIST:
            self.logger.warning(f'Command "{command}" not found!')
            return

        match command:
            case "play":
                if len(args) < 1:
                    print(len(args), args)
                    self.logger.warning(
                        f'Command "play" only takes 1 argument! Type: URL or Name of song!'
                    )
                    return
                self.mm.play(args[0])
                self.logger.info(f"Currently Playing: \n\t{self.mm.current_playing.title} by {self.mm.current_playing.artist} from their album {self.mm.current_playing.album}!")
            case "pause":
                self.mm.toggle_pause()
                self.logger.info(
                        f'{"Paused" if self.mm.musicplayer.pause else "Unpaused"} track {self.mm.current_playing.title}'
                    )
            case "exit":
                raise Die
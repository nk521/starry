import logging
from typing import Any, Coroutine
from rich.console import RenderableType

from textual import events
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Horizontal, Vertical
from textual.events import Key
from textual.widgets import Input, Static
from textual.color import Color

from Parser import Parser, Die
from TextHandler import TextHandler
import MusicManager as MM
from widgets import CommandInput, CurrentlyPlaying, LogWrapperWidget, TitleStatic


class Starry(App):
    """Searches a dictionary API as-you-type."""

    parserobj = Parser()

    BINDINGS = [
        Binding("ctrl+c", "do_nothing", "Quit", show=False, priority=True),
        Binding("tab", "do_nothing", "Focus Next", show=False, priority=True),
        Binding("shift+tab", "do_nothing", "Focus Previous", show=False, priority=True),
    ]

    def action_do_nothing(self):
        ...

    def on_ready(self) -> None:
        to_write = """
  [bold #f0f050]mm[bold #50f050]mm [bold #50f0f0]m[bold #5050f0]mm[bold #f050f0]mm[bold #f05050]mm   [bold #50f050]m[bold #50f0f0]m   [bold #f050f0]mm[bold #f05050]mm[bold #f0f050]m  [bold #50f050]m[bold #50f0f0]mm[bold #5050f0]mm [bold #f050f0]m     [bold #50f050]m
 [bold #f0f050]#[bold #50f050]"   [bold #5050f0]"   [bold #f05050]#      [bold #50f0f0]#[bold #5050f0]#   [bold #f05050]#   [bold #50f050]"# [bold #50f0f0]#   [bold #f050f0]"[bold #f05050]# [bold #f0f050]"m [bold #50f050]m[bold #50f0f0]" 
 [bold #50f050]"[bold #50f0f0]#m[bold #5050f0]mm    [bold #f0f050]#     [bold #5050f0]#  [bold #f050f0]#  [bold #f0f050]#m[bold #50f050]mm[bold #50f0f0]m" [bold #5050f0]#[bold #f050f0]mm[bold #f05050]mm[bold #f0f050]"  [bold #50f050]"[bold #50f0f0]#"  
     [bold #f050f0]"[bold #f05050]#   [bold #50f050]#     [bold #f050f0]#m[bold #f05050]m#  [bold #50f050]#   [bold #5050f0]"m [bold #f050f0]#   [bold #f0f050]"[bold #50f050]m   [bold #5050f0]#   
 [bold #5050f0]"[bold #f050f0]mm[bold #f05050]m#[bold #f0f050]"   [bold #50f0f0]#    [bold #f050f0]#    [bold #50f050]# [bold #50f0f0]#    [bold #f050f0]" [bold #f05050]#    [bold #50f0f0]"   [bold #f050f0]#   
"""
        self.logger = logging.getLogger("starrylogger")
        self.logger.setLevel(logging.DEBUG)
        th = TextHandler(self.logger_widget.richlog_widget)
        th.setLevel(logging.DEBUG)
        self.logger.addHandler(th)

        self.logger.info("Welcome to [bold blue][i]Starry[/i][/bold blue] 🎧 !")
        self.logger.debug("This is the logging section ...")

    CSS_PATH = "app.tcss"

    def compose(self) -> ComposeResult:
        self.result_static_widget: Static = Static(id="results")
        self.currently_playing: Static = Static("Currently Playing")
        self.music_progress_bar = CurrentlyPlaying(parserobj=self.parserobj)
        self.result_widget = Vertical(
            self.music_progress_bar, self.result_static_widget, classes="top-half"
        )
        # self.left_pane = Vertical(self.music_progress_bar, self.result_widget)
        
        self.title_widget = TitleStatic(classes="top-half")
        self.logger_widget = LogWrapperWidget()
        self.top_half = Horizontal(self.result_widget, self.logger_widget)

        self.input_widget = CommandInput()

        yield self.title_widget
        yield self.top_half
        yield self.input_widget
        # yield Footer()

    def on_mouse_scroll_up(self, event: events.MouseScrollUp):
        # increase volume
        ...

    def on_mouse_scroll_down(self, event: events.MouseScrollDown):
        # decrease volume
        ...

    def on_key(self, event: Key) -> None:
        match event.key:
            case "slash":
                self.set_focus(self.input_widget)
            case "escape":
                if self.focused == self.input_widget:
                    self.input_widget.blur()
            case "up":
                if not self.input_widget.has_focus:
                    MM.MPV.volume = min(MM.MPV.volume + 5, 100)
            case "down":
                if not self.input_widget.has_focus:
                    MM.MPV.volume = max(MM.MPV.volume - 5, 0)
            case "q":
                self.exit()
            case "_":
                ...

    async def on_input_submitted(self, message: Input.Submitted) -> None:
        if message.value:
            try:
                self.parserobj.parse(message.value)
            except Die:
                self.exit()

            self.input_widget.value = ""

    def exit(
        self,
        result: Any | None = None,
        return_code: int = 0,
        message: RenderableType | None = None,
    ) -> None:
        MM.MPV.quit(0)
        return super().exit(result, return_code, message)


if __name__ == "__main__":
    app = Starry()
    app.run()

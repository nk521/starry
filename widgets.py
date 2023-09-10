import logging
from textual.containers import Center, Horizontal, Middle, Vertical, VerticalScroll
import MusicManager as MM
from textual.reactive import reactive
from textual.widget import Widget
from Parser import Parser


from rich.highlighter import Highlighter
from textual import events
from textual.suggester import SuggestFromList, Suggester
from textual.validation import Validator
from textual.widgets import Input, ProgressBar, RichLog, Static


from typing import Iterable



class CommandInput(Input):
    BLUR_PLACEHOLDER = "Press '/' for command mode ..."
    FOCUS_PLACEHOLDER = "For help, just run `help`. Press `Esc` for normal mode ..."

    def __init__(
        self,
        value: str | None = None,
        placeholder: str = "",
        highlighter: Highlighter | None = None,
        password: bool = False,
        *,
        suggester: Suggester | None = None,
        validators: Validator | Iterable[Validator] | None = None,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
    ) -> None:
        placeholder = self.BLUR_PLACEHOLDER
        suggester = SuggestFromList(Parser.COMMANDS_LIST, case_sensitive=True)
        super().__init__(
            value,
            placeholder,
            highlighter,
            password,
            suggester=suggester,
            validators=validators,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    # def on_focused(self, event: events.):
    #     self.placeholder = self.FOCUS_PLACEHOLDER

    def on_focus(self, event: events.Focus):
        self.placeholder = self.FOCUS_PLACEHOLDER

    def on_blur(self, event: events.Blur):
        self.placeholder = self.BLUR_PLACEHOLDER


class TitleStatic(Static):
    def on_mount(self, event: events.Mount) -> None:
        self.id = "TitleWidget"
        self.styles.align_horizontal = "center"
        self.styles.text_align = "center"
        self.update_title_runner = self.set_interval(1 / 60, self.update_title)
    
    def update_title(self):
        self.update(f"[bold blue]Starry[/bold blue] 🎧 | Logged in as [i]\"{2}\"[/i]")


class LogWrapperWidget(VerticalScroll):
    class LogWidget(RichLog):
        def on_mount(self):
            self.styles.overflow_y = "auto"
            self.styles.overflow_x = "auto"

    richlog_widget = LogWidget(auto_scroll=True, markup=True, id="logger")

    def on_mount(self, event: events.Mount) -> None:
        self.classes = "top-half"
        self.mount(self.richlog_widget)
        self.styles.width = "30%"
        self.styles.overflow_y = "auto"
        self.styles.overflow_x = "auto"


class MusicProgress(ProgressBar):
    duration = reactive(0)
    cur_time = reactive(0)

    def __init__(
        self,
        total: float | None = None,
        *,
        show_bar: bool = True,
        show_percentage: bool = True,
        show_eta: bool = True,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        parserobj: Parser | None = None,
    ):
        self.parserobj = parserobj
        self.logger = logging.getLogger("starrylogger")
        super().__init__(
            total,
            show_bar=show_bar,
            show_percentage=show_percentage,
            show_eta=show_eta,
            name=name,
            id=id,
            classes=classes,
            disabled=disabled,
        )

    def update_progress(self) -> None:
        """Method to update time to current."""
        self.cur_time = MM.MPV.time_pos
        self.duration = MM.MPV.duration
        self.log.info(f"{self.cur_time, self.duration}")
        self.update(total=self.duration, progress=self.cur_time)


class CurrentlyPlaying(Vertical):
    duration = reactive(0)
    length = reactive(0)
    length_text = reactive("00:00")

    def __init__(
        self,
        *children: Widget,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
        disabled: bool = False,
        parserobj: Parser | None = None,
    ) -> None:
        self.parserobj = parserobj
        self.logger = logging.getLogger("starrylogger")
        self.music_text = Static("00:00/00:00", id="some")
        self.music_progress = MusicProgress(
            parserobj=self.parserobj,
            show_eta=False,
            show_percentage=False,
            id="musicprogress",
        )
        children = [x for x in children]

        self.name_of_song = Static("Hello 👋", classes="some2")
        self.bottom = Horizontal(self.music_progress, self.music_text, classes="some2")
        self.top = Vertical(self.bottom, self.name_of_song, classes="some2")

        # children.append(self.name)
        children.append(self.top)
        super().__init__(
            *children, name=name, id=id, classes=classes, disabled=disabled
        )

    def on_mount(self) -> None:
        """Event handler called when widget is added to the app."""
        self.update_stuff = self.set_interval(
            1 / 60, self.update_currently_playing, pause=False
        )

    def update_currently_playing(self) -> None:
        if not MM.CURR.cur_time > 0:
            return
        self.music_progress.update_progress()
        self.music_text.update(
            f"{MM.seconds_to_human(MM.MPV.time_pos)}/{MM.seconds_to_human(MM.MPV.duration)} (- {MM.MPV.seconds_to_human(MM.time_remaining)})"
        )
        self.name_of_song.update(
            f"Currently Playing:  Song - {MM.CURR.title} | Artist - {MM.CURR.artist} | Album - {MM.CURR.album}!"
        )
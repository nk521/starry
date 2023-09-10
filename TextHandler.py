from textual.widgets import RichLog


import logging


class TextHandler(logging.Handler):
    """Class for  logging to a TextLog widget"""

    def __init__(self, richlog_widget):
        # run the regular Handler __init__
        logging.Handler.__init__(self)
        # Store a reference to the Text it will log to
        self.richlog_widget: RichLog = richlog_widget

    def emit(self, record):
        msg = self.format(record)
        pre = ""
        match record.levelname:
            case "VERBOSE":
                pre = "[bold blue][V]"
            case "DEBUG":
                pre = "[bold green][D]"
            case "CRITICAL":
                pre = "[bold red][C]"
            case "ERROR":
                pre = "[bold red][E]"
            case "WARNING":
                pre = "[bold yellow][W]"
            case "INFO":
                pre = "[bold white][I]"

        self.richlog_widget.write(pre + " " + msg)
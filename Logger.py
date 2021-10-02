import logging
import os
from typing import Any

from rich.logging import RichHandler


class BotLogger(logging.getLoggerClass()):
    appname = "DelayBot"

    base_dir = "./log"
    log_file = "{0}/{1}.log".format(base_dir, appname)

    def debug(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).debug("{}[D]{} {}".format("[yellow3]", "[/yellow3]", msg))

    def verbose(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        if self.isEnabledFor(logging.getLevelName("VERBOSE")):
            self._log(logging.getLevelName("VERBOSE"), "{}[V]{} {}".format("[blue]", "[/blue]", msg), ())

    def info(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).info("{}[*]{} {}".format("[bold blue]", "[/bold blue]", msg))

    def warning(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).warning("{}[!]{} {}".format("[bold orange3]", "[/bold orange3]", msg))

    def error(self, msg: Any, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).error("{}[-]{} {}".format("[bold red]", "[/bold red]", msg))

    def exception(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).exception("{}[x]{} {}".format("[red3]", "[/red3]", msg))

    def critical(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        super(BotLogger, self).critical("{}[X]{} {}".format("[bold dark_red]", "[/bold dark_red]", msg))

    def success(self, *args: Any, **kwargs: Any) -> None:
        msg = ''
        for arg in args:
            msg += str(arg)
        if self.isEnabledFor(logging.getLevelName("SUCCESS")):
            self._log(logging.getLevelName("SUCCESS"),
                      "{}[+]{} {}".format("[bold green]", "[/bold green]", msg), ())


if not os.path.isfile(BotLogger.log_file):
    os.makedirs(BotLogger.base_dir, exist_ok=True)

logging.setLoggerClass(BotLogger)

logging.addLevelName(15, "VERBOSE")
logging.addLevelName(25, "SUCCESS")

# create file handler which logs even debug messages
file_handler = logging.FileHandler(BotLogger.log_file)
file_handler.setLevel(logging.DEBUG)

# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)

rich_handler = RichHandler(rich_tracebacks=True,
                           show_time=False,
                           markup=True,
                           show_level=False,
                           show_path=False)
rich_handler.setLevel(logging.INFO)

logging.basicConfig(
    format="%(message)s",
    handlers=[rich_handler, file_handler]
)

logger: BotLogger = logging.getLogger(BotLogger.appname)
logger.setLevel(logging.DEBUG)

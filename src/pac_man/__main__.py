from datetime import timedelta
import time
import logging
from pydantic import ValidationError
from rich.console import Console
from typing import ClassVar

from .utils import Config
from .loop import LoopMachine


class ElapsedFormatter(logging.Formatter):
    """Ensures correct time information on each logging."""

    COLORS: ClassVar[dict[int, str]] = {
        logging.DEBUG: "\x1b[0;90m",
        logging.INFO: "\x1b[36m",
        logging.WARNING: "\x1b[33m",
        logging.ERROR: "\x1b[31m"
    }
    RESET: ClassVar[str] = "\x1b[0m"

    def __init__(self) -> None:
        """Defines start time."""
        self.start_time = time.time()

    def format(self, record: logging.LogRecord) -> str:
        """Redefines logging formatting to include time."""
        elapsed_seconds = record.created - self.start_time
        elapsed = timedelta(seconds=elapsed_seconds)
        formated_elapsed = (f"{self.COLORS[logging.DEBUG]}"
                            f"[{elapsed}]{self.RESET}")

        color = self.COLORS.get(record.levelno, "")
        formated_level = f"{color}{record.levelname:<8}{self.RESET}"

        return f"{formated_elapsed} {formated_level} : {record.getMessage()}"

    @staticmethod
    def start_log() -> None:
        """Sets logging context and logs starting info."""
        handler: logging.StreamHandler = logging.StreamHandler()
        handler.setFormatter(ElapsedFormatter())
        logging.getLogger().addHandler(handler)

        log = logging.getLogger('PacMan')
        log.setLevel(5)
        log.info("Program start")


def main() -> int:
    """Main loop, sets up config and then main loop."""
    ElapsedFormatter.start_log()
    console = Console()

    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    try:
        with LoopMachine(config=config) as pacman:
            pacman.run()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    return 0


if __name__ == "__main__":
    main()

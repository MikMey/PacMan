from datetime import timedelta
import time

import logging
from pydantic import ValidationError
from rich.console import Console

from .utils import Config
from .render import SpriteSheetCache
from .loop import GameLoop, LoopMachine

class ElapsedFormatter():

    def __init__(self):
        self.start_time = time.time()

    def format(self, record: logging.LogRecord):
        elapsed_seconds = record.created - self.start_time
        #using timedelta here for convenient default formatting
        elapsed = timedelta(seconds = elapsed_seconds)
        return "{} {} - {}".format(elapsed, record.levelname, record.getMessage())

def start_log():
    #add custom formatter to root logger for simple demonstration
    handler = logging.StreamHandler()
    handler.setFormatter(ElapsedFormatter())
    logging.getLogger().addHandler(handler)

    log = logging.getLogger('PacMan')
    log.setLevel(5)
    log.info("Programm start")

def main() -> int:

    start_log()
    console = Console()

    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    with LoopMachine(config=config) as loop_machine:
        loop_machine.run_pacman()

    return 0


if __name__ == "__main__":
    main()
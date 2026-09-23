from .utils import Config
from .render import SpriteSheetCache
from .loop import GameLoop

from pydantic import ValidationError
from rich.console import Console
import time

from datetime import timedelta
import logging
import time

class ElapsedFormatter():

    def __init__(self):
        self.start_time = time.time()

    def format(self, record):
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

    game = GameLoop(config=config)

    try:
        asset_cache = SpriteSheetCache.from_default_file_path(
            scale_factor=game.scale_factor
        )
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    game.load_level(asset_cache=asset_cache)

    game.run()

    return 0


if __name__ == "__main__":
    main()
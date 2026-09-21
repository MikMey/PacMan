from .configuration import Config
from .spritesheet import SpriteSheetCache
from .game import Game

from pydantic import ValidationError
from rich.console import Console


def main() -> int:

    console = Console()

    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    game = Game(config=config)

    try:
        asset_cache = SpriteSheetCache.from_default_file_path(
            scale_factor=game.scale_factor
        )
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    game.load_level(asset_cache=asset_cache)

    game.loop()

    return 0


if __name__ == "__main__":
    main()
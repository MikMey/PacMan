from .configuration import Config
from .spritesheet import SpriteSheetCache
from .level import Level
from .hud import Hud

from mazegenerator import MazeGenerator
from pydantic import ValidationError
from rich.console import Console
import pygame


def main() -> int:

    console = Console()

    # Load and validate configuration file (NOTE: actually use it please lol)
    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    # Start up pygame (NOTE: dimensions may need to fit maze dimensions)
    pygame.init()
    screen = pygame.display.set_mode((1000, 1200))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    # Initialize and cache all needed sprites (NOTE: scaling messes up speed)
    TILE_SCREEN_FACTOR = 4
    try:
        asset_cache = SpriteSheetCache.from_default_file_path(
            scale_factor=TILE_SCREEN_FACTOR
        )
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    # Get Basic Tile Layout (tile metadata/sprites are untied for performance)
    maze_x, maze_y = 5, 5
    hex_matrix = MazeGenerator(size=(maze_x, maze_y)).maze

    # Initialize Level (NOTE: soon in a centralized main class?)
    hud = Hud(asset_cache=asset_cache, screen=screen)
    level = Level(
        hex_matrix=hex_matrix,
        asset_cache=asset_cache,
        screen=screen
    )

    # Main game loop (from which states (start_screen, main, ...) are called)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((176, 38, 255))
        hud.loop(dt)
        level.loop(dt)

        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    main()

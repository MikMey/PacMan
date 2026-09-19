from .configuration import Config
from .spritesheet import SpriteSheetCache
from .level import Level
from .hud import Hud
from .tile import TILE_SIZE

from mazegenerator import MazeGenerator
from pydantic import ValidationError
from rich.console import Console
import pygame
import math


def main() -> int:

    console = Console()

    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    # TARGET_MAX_W = 2000
    # TARGET_MAX_H = 2000
    # BASE_VERTICAL_PADDING = 60

    # scale_w = TARGET_MAX_W / (config.levels[0].width * TILE_SIZE)
    # scale_h = (TARGET_MAX_H / (config.levels[0].height * TILE_SIZE) +
    #            (2 * BASE_VERTICAL_PADDING))
    # TILE_SCREEN_FACTOR = min(3, max(1, math.floor(min(scale_w, scale_h))))

    # map_w = config.levels[0].width * TILE_SIZE * TILE_SCREEN_FACTOR
    # map_h = config.levels[0].height * TILE_SIZE * TILE_SCREEN_FACTOR

    # VERTICAL_PADDING = BASE_VERTICAL_PADDING * TILE_SCREEN_FACTOR
    # screen_w = int(map_w / 0.8)
    # screen_h = map_h + (2 * VERTICAL_PADDING)

    HORIZONTAL_PADDING_RATIO = 0.1
    VERTICAL_PADDING_ABS = 2 * TILE_SIZE

    screen_w, screen_h = 2000, 1500

    raw_level_w = config.levels[0].width * TILE_SIZE
    raw_level_h = config.levels[0].height * TILE_SIZE

    max_level_w = screen_w * (1 - HORIZONTAL_PADDING_RATIO)
    max_level_h = screen_h - VERTICAL_PADDING_ABS

    width_aligned_factor = int(max_level_w / raw_level_w)
    height_aligned_factor = int(max_level_h / raw_level_h)

    tile_screen_factor = min(15, max(1, min(width_aligned_factor,
                                     height_aligned_factor)))

    level_w = raw_level_w * tile_screen_factor
    level_h = raw_level_h * tile_screen_factor

    screen_w = int(level_w / (1 - HORIZONTAL_PADDING_RATIO))
    screen_h = level_h + (VERTICAL_PADDING_ABS * tile_screen_factor)

    vertical_padding = (screen_h - level_h) // 2
    horizontal_padding = (screen_w - level_w) // 2

    pygame.init()
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    try:
        asset_cache = SpriteSheetCache.from_default_file_path(
            scale_factor=tile_screen_factor
        )
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    # Get Basic Tile Layout (tile metadata/sprites are untied for performance)
    maze_x, maze_y = config.levels[0].width, config.levels[0].height
    hex_matrix = MazeGenerator(size=(maze_x, maze_y)).maze

    # Initialize Level (NOTE: soon in a centralized main class?)
    hud = Hud(
        asset_cache=asset_cache,
        screen=screen,
        vertical_padding=vertical_padding
    )
    level = Level(
        hex_matrix=hex_matrix,
        asset_cache=asset_cache,
        screen=screen,
        horizontal_padding=horizontal_padding,
        vertical_padding=vertical_padding
    )

    # Main game loop (from which states (start_screen, main, ...) are called)
    running = True
    while running:
        dt = clock.tick(60) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((100, 50, 255))
        hud.loop(dt)
        level.loop(dt)

        pygame.display.flip()

    pygame.quit()
    return 0


if __name__ == "__main__":
    main()

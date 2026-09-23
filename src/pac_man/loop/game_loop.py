import pygame

from mazegenerator import MazeGenerator

from ..utils import Config
from ..render import Hud, SpriteSheetCache
from ..models import TILE_SIZE

from .level import Level
from .states import State

class GameLoop(State):

    def __init__(self, config: Config) -> None:

        self.config = config

        pygame.init()

        max_win_w = pygame.display.Info().current_w * 0.8
        max_win_h = pygame.display.Info().current_h * 0.8

        level_cols = config.levels[0].width
        level_rows = config.levels[0].height

        raw_level_w = level_cols * TILE_SIZE
        raw_level_h = level_rows * TILE_SIZE

        max_level_w = int(max_win_w * 0.8)
        max_level_h = max_win_h - (2 * TILE_SIZE)

        self.scale_factor = min(
            max_level_w // raw_level_w,
            max_level_h // raw_level_h,
            8,
        )

        level_screen_w = int(raw_level_w * self.scale_factor)
        level_screen_h = int(raw_level_h * self.scale_factor)

        self.horizontal_padding = int(level_screen_w * 0.1)
        self.vertical_padding = int(TILE_SIZE * self.scale_factor)

        screen_w = level_screen_w + (2 * self.horizontal_padding)
        screen_h = level_screen_h + (2 * self.vertical_padding)

        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()

    def load_level(self, asset_cache: SpriteSheetCache) -> None:

        hex_matrix = MazeGenerator(
            size=(
                self.config.levels[0].width,
                self.config.levels[0].height
            )
        ).maze

        self.hud = Hud(
            asset_cache=asset_cache,
            screen=self.screen,
            vertical_padding=self.vertical_padding
        )
        self.level = Level(
            hex_matrix=hex_matrix,
            asset_cache=asset_cache,
            screen=self.screen,
            hud=self.hud,
            horizontal_padding=self.horizontal_padding,
            vertical_padding=self.vertical_padding
        )

    def run(self) -> None:

        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # self.screen.fill((100, 50, 255))
            self.hud.loop(dt)
            self.level.loop(dt)

            pygame.display.flip()

        pygame.quit()
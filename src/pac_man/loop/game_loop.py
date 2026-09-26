import pygame
import logging

from mazegenerator import MazeGenerator

from ..utils import Config
from ..render import Hud, SpriteSheetCache
from ..models import TILE_SIZE

from .level import Level
from .states import State

class GameLoop(State):

    def init_screen(self) -> tuple:
        screen_w = pygame.display.Info().current_w * 0.8
        screen_h = pygame.display.Info().current_h * 0.8

        self.screen = pygame.display.set_mode((screen_w, screen_h))
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()


    def init_level_size(self, width, height, screen_w, screen_h):

        level_cols = width
        level_rows = height

        raw_level_h = level_rows * TILE_SIZE
        raw_level_w = level_cols * TILE_SIZE

        max_level_w = int(screen_w * 0.8)
        max_level_h = screen_h - (2 * TILE_SIZE)

        self.scale_factor = min(
            max_level_w // raw_level_w,
            max_level_h // raw_level_h,
            8,
        )

        level_screen_w = int(raw_level_w * self.scale_factor)
        level_screen_h = int(raw_level_h * self.scale_factor)

        self.horizontal_padding = int(level_screen_w * 0.1)
        self.vertical_padding = int(TILE_SIZE * self.scale_factor)


    def __init__(self, config: Config) -> None:
        self.init_screen()
        self.init_level_size(
            config.levels[0].width,
            config.levels[0].height,
            self.screen.get_width(),
            self.screen.get_height()
        )


    def load_level(self, asset_cache: SpriteSheetCache, width, height) -> None:

        hex_matrix = MazeGenerator(
            size=(
                width,
                height
            )
        ).maze
        # log = logging.getLogger('PacMan')
        # log.debug(f'hex_matrix={hex_matrix}')

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

    def handle_input(self, key_event: pygame.event.Event) -> None:
        """Handle Cheats and color cycling.

        Parameters
        ----------
        key_event : pygame.event.Event
            Event of the KEYDOWN type which holds the held key.

        """
        match key_event.key:
            case pygame.K_KP7:
                next = self.hud.asset_cache.text_color_offset + 1
                self.hud.asset_cache.text_color_offset = next % 19
                self.hud.asset_cache.bake_text_offset(
                    self.hud.asset_cache.text_color_offset
                )
                self.hud.populate_sprite_groups()

            case pygame.K_KP8:
                next = self.hud.asset_cache.tile_color_offset + 1
                self.hud.asset_cache.tile_color_offset = next % 19
                self.hud.asset_cache.bake_tile_offset(
                    self.hud.asset_cache.tile_color_offset
                )
                self.level.reload_tile_sheet()

    def run(self, state) -> None:

        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    state.end_game()
                    running = False

                elif event.type == pygame.KEYDOWN:
                    self.handle_input(event)

            # self.screen.fill((100, 50, 255))
            self.hud.loop(dt)
            self.level.loop(dt)

            pygame.display.flip()

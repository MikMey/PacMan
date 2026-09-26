import pygame
import logging


from mazegenerator import MazeGenerator

from ..utils import Config
from ..render import Hud, SpriteSheetCache
from ..models import TILE_SIZE

from .level import Level
from .states import State

class GameLoop(State):
    """
    Runs between main screen and win or loose,
    handles level calling, score totaling and state changes
    """
    def __init__(self, config: Config, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.config = config
        self.screen = screen
        self.clock = clock
        self.load_level(
            width=self.config.levels[0].width,
            height=self.config.levels[0].height
        )

    def load_level(self, width, height) -> None:

        
                hex_matrix = MazeGenerator(
                    size=(
                        width,
                        height
                    )
                ).maze
                # log = logging.getLogger('PacMan')
                # log.debug(f'hex_matrix={hex_matrix}')
        
                self.level = Level(
                    hex_matrix=hex_matrix,
                    screen=self.screen,
                    columns=width,
                    rows=height
                )

                self.hud = Hud(
                    asset_cache=self.level.asset_cache,
                    screen=self.screen,
                    vertical_padding=self.level.vertical_padding
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

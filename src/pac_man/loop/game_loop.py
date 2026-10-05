import sys
from enum import Enum, auto

import logging
import pygame

from mazegenerator import MazeGenerator

from ..utils import Config
from ..render import Hud

from .level import Level
from .states import State

class GameState(Enum):
    LOAD_LEVEL = auto()
    RUN_LEVEL = auto()
    RESPAWN_LEVEL = auto()
    PAUSE = auto()
    PLAYER_DEATH = auto()
    GAME_OVER = auto()

class GameLoop(State):
    """
    Runs between main screen and win or loose,
    handles level calling, score totaling and state changes
    """
    def __init__(self, config: Config, screen: pygame.Surface, clock: pygame.time.Clock) -> None:
        self.log = logging.getLogger('PacMan')
        self.config = config
        self.screen = screen
        self.clock = clock

    def load_level(self, width, height) -> None:
        """Clear screen, get matrix, init hud and level, draw"""

        self.screen.fill(0)
        pygame.display.flip()

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
        self.level.render()
        self.hud.render()

    def pause(self):
        """Keep state until button is pressed"""
        self.level.render()
        self.hud.render()
        self.handle_event()

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

            case pygame.K_RETURN:
                self.state = GameState.LOAD_LEVEL

            case pygame.K_SPACE:
                self.state = GameState.PAUSE

            case pygame.K_ESCAPE:
                sys.exit()

            case _:
                self.state = GameState.RUN_LEVEL

    def run(self) -> None:
        """Finite State Machine for level based/gameloop logic"""
        self.state = GameState.LOAD_LEVEL
        level = 0
        self.lives = 3

        while self.state != GameState.GAME_OVER:

            dt = self.clock.tick(60) / 1000.0
            match self.state:

                case GameState.LOAD_LEVEL:
                    # self.log.debug('Enter LOAD_LEVEL')
                    if len(self.config.levels) > level:
                        width = self.config.levels[level].width
                        height = self.config.levels[level].height
                    else:
                        width = self.config.default_level.width
                        height = self.config.default_level.height

                    self.load_level(
                        width=width,
                        height=height
                    )
                    level += 1
                    self.state = GameState.PAUSE

                case GameState.RUN_LEVEL:
                    # self.log.debug('Enter RUN_LEVEL')
                    self.dstart = 0
                    self.handle_event()

                    alive = self.level.run(dt)
                    self.hud.loop(dt)
                    if not alive:
                        self.state = GameState.PLAYER_DEATH

                case GameState.RESPAWN_LEVEL:
                    # self.log.debug('Enter RESPAWN_LEVEL')
                    self.dstart += dt
                    self.level.pacman.kill(dt)
                    self.level.render()
                    if self.dstart > 1:
                        self.level.init_characters()
                        self.state = GameState.PAUSE

                case GameState.PAUSE:
                    # self.log.debug('Enter PAUSE')

                    self.pause()

                case GameState.PLAYER_DEATH:
                    # self.log.debug('Enter PLAYER_DEATH')
                    self.lives -= 1
                    if self.lives > 0:
                        self.state = GameState.RESPAWN_LEVEL
                    else:
                        self.state = GameState.GAME_OVER

            pygame.display.flip()

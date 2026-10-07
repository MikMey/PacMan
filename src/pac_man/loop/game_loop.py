import sys
from enum import Enum, auto

import logging
import pygame
import random
import sys

from mazegenerator import MazeGenerator

from ..utils import Config
from ..utils.configuration import LevelMetadata
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
    def __init__(self,
                 config: Config,
                 screen: pygame.Surface,
                 clock: pygame.time.Clock
                 ) -> None:
        self.log = logging.getLogger('PacMan')
        self.config = config
        self.screen = screen
        self.clock = clock

    def load_level(self, level_num: int) -> None:
        """Clear screen, get matrix, init hud and level, draw"""

        self.screen.fill(0)
        pygame.display.flip()

        level: LevelMetadata = self.config.levels[level_num]

        if level.seed is None:
            seed = random.randint(-sys.maxsize - 1, sys.maxsize)
        else:
            seed = level.seed

        try:
            hex_matrix = MazeGenerator(
                size=(level.width, level.height),
                seed=seed
            ).maze
        except Exception as err:
            sys.exit(f"Mazegen skillissue:\n{err}")

        self.level: Level = Level(
            hex_matrix=hex_matrix,
            screen=self.screen,
            level=level
        )

        self.hud = Hud(
            screen=self.screen,
            vertical_padding=self.level.vertical_padding,
            high_score=self.highscore,
            lives=self.lives
        )
        self.level.render()
        self.hud.render()

    def pause(self) -> None:
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

            case pygame.K_KP1:
                self.level.pacman.kill(self.dt)

            case pygame.K_KP2:
                self.lives += 1
                if self.hud:
                    self.hud.update_lives(self.lives)

            case pygame.K_KP3:
                if self.level and not self.level.freeze:
                    self.level.freeze = True
                elif self.level:
                    self.level.freeze = False

            case pygame.K_PAGEUP:
                if self.level:
                    self.level.pacman.speed += 1

            case pygame.K_PAGEDOWN:
                if self.level and self.level.pacman.speed >= 1:
                    self.level.pacman.speed -= 1

            case _:
                self.state = GameState.RUN_LEVEL

    def run(self, highscore: int) -> None:
        """Finite State Machine for level based/gameloop logic"""
        self.state = GameState.LOAD_LEVEL
        curr_level = 0
        self.lives = 3
        self.highscore = highscore

        while self.state != GameState.GAME_OVER:

            self.dt = self.clock.tick(60) / 1000.0
            match self.state:

                case GameState.LOAD_LEVEL:
                    # self.log.debug('Enter LOAD_LEVEL')
                    if len(self.config.levels) > curr_level:
                        lvl_conf = self.config.levels[curr_level]
                    else:
                        lvl_conf = self.config.default_level
                    # width = lvl_conf.width
                    # height = lvl_conf.height

                    self.load_level(level_num=curr_level)
                    self.limit = lvl_conf.timer
                    curr_level += 1
                    self.state = GameState.PAUSE

                case GameState.RUN_LEVEL:
                    # self.log.debug('Enter RUN_LEVEL')
                    self.limit -= self.dt
                    if self.limit <= 0:
                        self.state = GameState.GAME_OVER
                        continue
                    self.dstart = 0
                    self.handle_event()

                    alive = self.level.run(self.dt)
                    self.hud.loop(self.dt)
                    if not alive:
                        self.state = GameState.PLAYER_DEATH

                case GameState.RESPAWN_LEVEL:
                    # self.log.debug('Enter RESPAWN_LEVEL')
                    self.dstart += self.dt
                    self.level.pacman.kill(self.dt)
                    self.level.render()
                    if self.dstart > 1:
                        self.level.init_characters()
                        self.hud.update_lives(self.lives)
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

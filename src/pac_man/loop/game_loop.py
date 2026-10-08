import sys
from enum import Enum, auto

import logging
import pygame
import random

from mazegenerator import MazeGenerator

from ..utils import Config
from ..utils.configuration import LevelMetadata
from ..render import Hud
from ..models import PlayerState

from .level import Level
from .states import State, LoopState


class GameState(Enum):
    LOAD_LEVEL = auto()
    RUN_LEVEL = auto()
    RESPAWN_LEVEL = auto()
    PAUSE = auto()
    PLAYER_DEATH = auto()
    GAME_OVER = auto()
    RETURN = auto()


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

        level_data: LevelMetadata = self.config.levels[level_num]

        if level_data.seed is None:
            seed = random.randint(-sys.maxsize - 1, sys.maxsize)
        else:
            seed = level_data.seed

        try:
            hex_matrix = MazeGenerator(
                size=(level_data.width, level_data.height),
                seed=seed
            ).maze
        except Exception as err:
            sys.exit(f"Mazegen skillissue:\n{err}")

        self.level: Level = Level(
            hex_matrix=hex_matrix,
            screen=self.screen,
            level=level_data,
            config=self.config
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
        # self.handle_event()

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
                next = self.level.asset_cache.tile_color_offset + 1
                self.level.asset_cache.tile_color_offset = next % 19
                self.level.asset_cache.bake_tile_offset(
                    self.level.asset_cache.tile_color_offset
                )
                self.level.reload_tile_sheet()

            case pygame.K_RETURN:
                self.state = GameState.LOAD_LEVEL

            case pygame.K_SPACE:
                self.state = GameState.PAUSE

            case pygame.K_ESCAPE:
                self.state = GameState.RETURN

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

            case pygame.K_KP5:
                if self.level:
                    self.level.switch_ghosts()

            case _:
                self.state = GameState.RUN_LEVEL

    def set_state(self, new_state: GameState) -> None:
        """Sets self.state to a new GameState.

        Parameters
        ----------
        new_state : GameState
            New state of self.state.

        """
        self.log.debug(f"GameLoop: Setting {new_state.name}...")
        self.state = new_state

    def run(self, highscore: int, level_num: int) -> LoopState:
        """Finite State Machine for level based/gameloop logic."""
        self.state: GameState = GameState.LOAD_LEVEL
        # curr_level = 0
        self.lives = self.config.levels[level_num].lives
        self.highscore = highscore

        while self.state != GameState.RETURN:

            self.dt = self.clock.tick(60) / 1000.0
            self.handle_event()

            match self.state:

                case GameState.LOAD_LEVEL:
                    if level_num >= self.config.level_count:
                        return LoopState.WIN_SCREEN

                    # lvl_conf = self.config.levels[curr_level]
                    self.load_level(level_num=level_num)
                    self.hud.time = self.config.levels[level_num].timer + 1
                    self.hud.update_time_second()
                    level_num += 1
                    self.set_state(GameState.PAUSE)

                case GameState.RUN_LEVEL:
                    self.dstart: float = 0

                    is_no_pacgums = self.level.run(self.dt)
                    if self.level.pacman.state != PlayerState.ALIVE:
                        self.set_state(GameState.PLAYER_DEATH)
                    if is_no_pacgums:
                        self.set_state(GameState.LOAD_LEVEL)

                    if self.hud.loop(self.dt):
                        self.state = GameState.PLAYER_DEATH

                case GameState.RESPAWN_LEVEL:
                    self.dstart += self.dt
                    self.level.pacman.kill(self.dt)
                    self.level.render()
                    self.hud.time = self.config.levels[level_num].timer
                    if self.dstart > 1:
                        self.level.init_characters()
                        self.hud.update_lives(self.lives)
                        self.set_state(GameState.PAUSE)

                case GameState.PAUSE:
                    self.pause()

                case GameState.PLAYER_DEATH:
                    self.lives -= 1
                    if self.lives <= 0:
                        return LoopState.DEATH_SCREEN
                    self.set_state(GameState.RESPAWN_LEVEL)
                    # if self.lives > 0:
                    #     self.set_state(GameState.RESPAWN_LEVEL)
                    # else:
                    #     self.set_state(GameState.GAME_OVER)

            pygame.display.flip()
        return LoopState.MAIN_MENU

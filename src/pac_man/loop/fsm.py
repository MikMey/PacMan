from enum import Enum, auto

import logging
import pygame

from .game_loop import GameLoop
from .main_menu import MainMenu
from .death_screen import DeathScreen
from .win_screen import WinScreen

class LoopState(Enum):
    MAIN_MENU = auto()
    GAME_LOOP = auto()
    DEATH_SCREEN = auto()
    WIN_SCREEN = auto()
    END_GAME = auto()

class LoopMachine():
    state: LoopState = LoopState.MAIN_MENU

    def __init__(self, config):
        self.log = logging.getLogger('PacMan')
        self.config = config

    def __enter__(self):
        """context manager on call (basically init)"""
        self.log.info("context manager start")
        pygame.init()
        self.init_screen()
        self.game_loop = GameLoop(config=self.config, screen=self.screen, clock=self.clock)
        self.main_menu = MainMenu()
        self.death_screen = DeathScreen()
        self.win_screen = WinScreen()
        return self

    def __exit__(self, exc_type, exc, tb):
        """context manager safe exit"""
        pygame.quit()
        self.log.info("context manager end")

    def init_screen(self) -> tuple:
        self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()

    def run_pacman(self):
        """Finite State machine for entirety of pacman"""

        while self.state != LoopState.END_GAME:

            match self.state:
                case LoopState.MAIN_MENU:
                    self.log.debug("Enter MainMenu")
                    self.main_menu.run()
                    self.state = LoopState.GAME_LOOP

                case LoopState.GAME_LOOP:
                    self.log.debug("Enter GameLoop")
                    self.game_loop.run()

                case LoopState.DEATH_SCREEN:
                    self.log.debug("Enter DeathScreen")
                    self.death_screen.run()

                case LoopState.WIN_SCREEN:
                    self.log.debug("Enter WinScreen")
                    self.win_screen.run()


from enum import Enum

import logging
import pygame

from .game_loop import GameLoop
from .main_menu import MainMenu
from .death_screen import DeathScreen
from .win_screen import WinScreen

class LoopStates():
    MAIN_MENU = 0
    GAME_LOOP = 1
    DEATH_SCREEN = 2
    WIN_SCREEN = 3
    END_GAME = 4
    NEW_LEVEL = 5

    def __init__(self):
        self._state = LoopStates.MAIN_MENU

    def main_menu(self):
        self._state = LoopStates.MAIN_MENU

    def game_loop(self):
        self._state = LoopStates.GAME_LOOP

    def death_screen(self):
        self._state = LoopStates.DEATH_SCREEN

    def win_screen(self):
        self._state = LoopStates.WIN_SCREEN

    def end_game(self):
        self._state = LoopStates.END_GAME

    def new_level(self):
        self._state = LoopStates.NEW_LEVEL

    def get_state(self):
        return self._state

class LoopMachine():
    state: LoopStates = LoopStates()

    def __init__(self, config):
        self.log = logging.getLogger('PacMan')
        self.config = config

    def __enter__(self):
        self.log.info("context manager start")
        pygame.init()
        self.game_loop = GameLoop(config=self.config)
        self.main_menu = MainMenu()
        self.death_screen = DeathScreen()
        self.win_screen = WinScreen()
        return self

    def __exit__(self, exc_type, exc, tb):
        pygame.quit()
        self.log.info("context manager end")

    def run_gameloop(self, asset_cache):
        while True:
            match self.state.get_state():

                case LoopStates.MAIN_MENU:
                    self.log.debug('Enter MainMenu')
                    self.main_menu.run()
                    self.state.new_level()

                case LoopStates.GAME_LOOP:
                    self.log.debug('Enter GameLoop')
                    self.game_loop.run(self.state)

                case LoopStates.DEATH_SCREEN:
                    self.log.debug('Enter DeathScreen')
                    self.death_screen.run()

                case LoopStates.WIN_SCREEN:
                    self.log.debug('Enter WinScreen')
                    self.win_screen.run()

                case LoopStates.END_GAME:
                    self.log.debug('Enter Close')
                    return

                case LoopStates.NEW_LEVEL:
                    self.game_loop.load_level(asset_cache)
                    self.log.debug('Enter NewLevel')
                    self.state.game_loop()







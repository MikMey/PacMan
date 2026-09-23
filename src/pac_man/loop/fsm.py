from enum import Enum

import logging

from .game_loop import GameLoop
from .main_menu import MainMenu
from .death_screen import DeathScreen
from .win_screen import WinScreen

class LoopStates(Enum):
	MAIN_MENU = 0
	GAME_LOOP = 1
	DEATH_SCREEN = 2
	WIN_SCREEN = 3
	END_GAME = 4
	NEW_LEVEL = 5

class LoopMachine():
	state: LoopStates = LoopStates.MAIN_MENU

	def __init__(self, config):
		self.config = config
		self.game_loop = GameLoop(config=config)
		self.main_menu = MainMenu()
		self.death_screen = DeathScreen()
		self.win_screen = WinScreen()

	def run_gameloop(self, asset_cache):
		log = logging.getLogger('PacMan')
		while True:
			match self.state:

				case LoopStates.MAIN_MENU:
					log.debug('Enter MainMenu')
					self.state = LoopStates.GAME_LOOP
					continue
					self.main_menu.run()

				case LoopStates.GAME_LOOP:
					log.debug('Enter GameLoop')
					self.game_loop.load_level(asset_cache)
					self.game_loop.run()
					self.state = LoopStates.END_GAME

				case LoopStates.DEATH_SCREEN:
					log.debug('Enter DeathScreen')
					self.death_screen.run()

				case LoopStates.WIN_SCREEN:
					log.debug('Enter WinScreen')
					self.win_screen.run()

				case LoopStates.END_GAME:
					log.debug('Enter Close')
					return

				case LoopStates.NEW_LEVEL:
					log.debug('Enter NewLevel')






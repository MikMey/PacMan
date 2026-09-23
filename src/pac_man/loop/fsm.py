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

class LoopMachine():
	state: LoopStates = LoopStates.MAIN_MENU

	def __init__(self):
		self.game_loop = GameLoop()
		self.main_menu = MainMenu()
		self.death_screen = DeathScreen()
		self.win_screen = WinScreen()

	def run_gameloop(self):
		log = logging.getLogger('PacMan')
		while True:
			match self.state:
				case LoopStates.MAIN_MENU:
					log.debug('Enter MainMenu')
					self.main_menu.run()
				case LoopStates.GAME_LOOP:
					log.debug('Enter GameLoop')
					self.game_loop.run()
				case LoopStates.DEATH_SCREEN:
					log.debug('Enter DeathScreen')
					self.death_screen.run()
				case LoopStates.WIN_SCREEN:
					log.debug('Enter WinScreen')
					self.win_screen.run()
				case LoopStates.END_GAME:
					return





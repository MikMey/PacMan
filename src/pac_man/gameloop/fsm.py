from enum import Enum

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
		pass

	def run_gameloop(self):
		while True:
			match self.state:
				case LoopStates.MAIN_MENU:
					self._main_menu()
				case LoopStates.GAME_LOOP:
					self._game_loop()
				case LoopStates.DEATH_SCREEN:
					self._death_screen()
				case LoopStates.WIN_SCREEN:
					self._win_screen()
				case LoopStates.END_GAME:
					return





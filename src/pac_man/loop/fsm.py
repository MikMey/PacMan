from .states import State
from .game_loop import GameLoop
from .main_menu import MainMenu
from .death_screen import DeathScreen
from .win_screen import WinScreen
from ..utils.configuration import Config

from enum import Enum, auto
from typing import Optional
from types import TracebackType
import logging
import pygame


class LoopState(Enum):
    """Enum of rendering/logic game states.

    Attributes
    ----------
    MAIN_MENU
        Start up screen that explains the movement and shows the leaderboard.
    GAME_LOOP
        Main level loop dealing with player and ghost movement and rendering.
    DEATH_SCREEN
        Screen that shows a losing message and the leaderboard. TODO
    WIN_SCREEN
        Screen that shows a winning message and the leaderboard. TODO
    END_GAME
        ? TODO

    """
    MAIN_MENU = auto()
    GAME_LOOP = auto()
    DEATH_SCREEN = auto()
    WIN_SCREEN = auto()
    END_GAME = auto()


class LoopMachine(State):
    """Project implementation of a Finite State Machine.

    This class should only be used via the 'with' keyword.

    Parameters
    ----------
    config : :obj:`Config`
        Class that holds game logic configrations.

    Attributes
    ----------
    state : :obj:`LoopState`
        Current game state.

    """
    state: LoopState = LoopState.MAIN_MENU

    def __init__(self, config: Config) -> None:
        """Sets up logging context and passes game configurations."""
        self._log = logging.getLogger('PacMan')
        self._config = config

    def __enter__(self) -> "LoopMachine":
        """Initializes pygame and instantiates game state classes.

        Note
        ----
        This should only be used as part of a context manager ('with' keyword).

        """
        self._log.info("Starting LoopMachine...")

        pygame.init()
        self._init_screen()
        self.game_loop = GameLoop(
            config=self._config,
            screen=self.screen,
            clock=self.clock
        )
        self.main_menu = MainMenu()
        self.death_screen = DeathScreen()
        self.win_screen = WinScreen()
        return self

    def __exit__(self,
                 type_: Optional[type[BaseException]],
                 value: Optional[BaseException],
                 traceback: Optional[TracebackType]) -> None:
        """Safely quits pygame.

        Note
        ----
        This should only be used as part of a context manager ('with' keyword).

        """
        self._log.info("Quitting LoopMachine...")
        pygame.quit()

    def _init_screen(self) -> None:
        """Sets screen and clock attributes, and window caption."""
        self.screen = pygame.display.set_mode(flags=pygame.FULLSCREEN)
        pygame.display.set_caption("Pac-Man")
        self.clock = pygame.time.Clock()

    def run(self) -> None:
        """Finite State machine for entirety of PacMan."""
        while self.state != LoopState.END_GAME:
            self.handle_event()

            match self.state:
                case LoopState.MAIN_MENU:
                    self._log.debug("Enter State: MAIN_MENU")
                    self.main_menu.run()
                    self.state = LoopState.GAME_LOOP

                case LoopState.GAME_LOOP:
                    self._log.debug("Enter State: GAME_LOOP")
                    self.game_loop.run()
                    self.state = LoopState.DEATH_SCREEN

                case LoopState.DEATH_SCREEN:
                    self._log.debug("Enter State: DEATH_SCREEN")
                    self.death_screen.run()

                case LoopState.WIN_SCREEN:
                    self._log.debug("Enter State: WIN_SCREEN")
                    self.win_screen.run()

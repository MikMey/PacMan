from typing import Optional
from types import TracebackType
import logging
import pygame

from ..utils import Config
from ..render import Hud
from .game_loop import GameLoop
from .main_menu import MainMenu
from .death_screen import DeathScreen
from .win_screen import WinScreen
from .states import State, LoopState
from .highscore import EnterHighscore, ShowHighscore, Guide


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
        self.main_menu = MainMenu(screen=self.screen)
        self.death_screen = DeathScreen()
        self.win_screen = WinScreen()
        self.enter_highscore =\
            EnterHighscore(self._config.highscore_filename, self.screen)
        self.show_highscore = ShowHighscore(None, None)
        self.guide = Guide(None, None)
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
            self.screen.fill(0)

            match self.state:
                case LoopState.MAIN_MENU:
                    self.state = self.main_menu.run()

                case LoopState.GAME_LOOP:
                    self.game_loop = GameLoop(
                        config=self._config,
                        screen=self.screen,
                        clock=self.clock
                    )
                    self.state = self.game_loop.run(ShowHighscore.highscore, 0)

                case LoopState.DEATH_SCREEN:
                    self._log.debug("Enter State: DEATH_SCREEN")
                    self.death_screen.run()
                    self.state = LoopState.ENTER_HIGHSCORE

                case LoopState.WIN_SCREEN:
                    self._log.debug("Enter State: WIN_SCREEN")
                    self.win_screen.run()
                    self.state = LoopState.ENTER_HIGHSCORE

                case LoopState.SHOW_HIGHSCORE:
                    self.state = self.show_highscore.run()

                case LoopState.ENTER_HIGHSCORE:
                    self.enter_highscore.run(Hud.score)
                    Hud.score = 0
                    self.show_highscore = ShowHighscore(None, None)
                    self.state = LoopState.SHOW_HIGHSCORE

                case LoopState.GUIDE:
                    self.state = self.guide.run()

            pygame.display.flip()

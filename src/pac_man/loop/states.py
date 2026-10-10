from abc import ABC, abstractmethod
import sys
from enum import Enum, auto
from typing import Any
import pygame

from ..models import StaticSpriteElement
from ..render import SpriteSheetCache

SUBTILE_SIZE = 8


class LoopState(Enum):
    """All finite states outside of the main gameplay loop.

    Parameters
    ----------
    MAIN_MENU
        State that shows options with a selector.
    GAME_LOOP
        Main gameplay loop. More substates in game_loop.py.
    DEATH_SCREEN
        Passes immedietely to ENTER_HIGHSCORE.
    WIN_SCREEN
        Passes immedietely to ENTER_HIGHSCORE.
    END_GAME
        Stopping condition for main run loop.
    SHOW_HIGHSCORE
        Shows the leaderboard of highscore json file.
    ENTER_HIGHSCORE
        Allows entering name for score to be added to highscore file.
    GUIDE
        Displays control information.

    """
    MAIN_MENU = auto()
    GAME_LOOP = auto()
    DEATH_SCREEN = auto()
    WIN_SCREEN = auto()
    END_GAME = auto()
    SHOW_HIGHSCORE = auto()
    ENTER_HIGHSCORE = auto()
    GUIDE = auto()


class State(ABC):
    """Abstract class that defines a finite state."""

    def __init__(self, state: LoopState | Any) -> None:
        """Assigns current state name/enum."""
        self.state = state

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any:
        """Called by the Finite State Machine each frame."""
        pass

    def handle_input(self, key_event: pygame.event.Event) -> None:
        """Checks for key_events. Usually always re-set.

        Parameters
        ----------
        key_event : pygame.event.Event
            Class filled with pressed keys.

        """
        match key_event.key:
            case pygame.K_ESCAPE:
                match self.state:
                    case LoopState.SHOW_HIGHSCORE:
                        self.state = LoopState.MAIN_MENU
                    case LoopState.GUIDE:
                        self.state = LoopState.MAIN_MENU
                    case (LoopState.DEATH_SCREEN | LoopState.WIN_SCREEN):
                        self.state = LoopState.ENTER_HIGHSCORE
                    case _:
                        sys.exit()
            case pygame.K_RETURN:
                match self.state:
                    case LoopState.SHOW_HIGHSCORE:
                        self.state = LoopState.MAIN_MENU
                    case LoopState.GUIDE:
                        self.state = LoopState.MAIN_MENU
                    case (LoopState.DEATH_SCREEN | LoopState.WIN_SCREEN):
                        self.state = LoopState.ENTER_HIGHSCORE
            case pygame.K_KP1:
                self.state = LoopState.MAIN_MENU
            case pygame.K_KP2:
                self.state = LoopState.ENTER_HIGHSCORE
            case pygame.K_KP3:
                self.state = LoopState.DEATH_SCREEN
            case pygame.K_KP4:
                self.state = LoopState.WIN_SCREEN

    def handle_event(self) -> None:
        """handle different types of pygame events"""
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                sys.exit()

            elif pygame_event.type == pygame.KEYDOWN:
                self.handle_input(pygame_event)

    @staticmethod
    def _group_add_str(
        cache: SpriteSheetCache,
        group: pygame.sprite.Group,
        s: str,
        pos: list
    ) -> None:
        """Adds a character sprite to a group.

        Parameters
        ----------
        cache : SpriteSheetCache
            Cache class to get sprite from.
        group : pygame.sprite.Group
            Group to add sprite to.
        s : str
            Name of sprite.
        pos : list
            Location of sprite [x, y].

        """
        for char in s:
            group.add(
                StaticSpriteElement.from_pixel(
                    cache.get_static("CHAR-" + char.upper()),
                    pos[0] * cache.scale_factor * SUBTILE_SIZE,
                    pos[1] * cache.scale_factor * SUBTILE_SIZE
                )
            )
            pos[0] += 1

    @staticmethod
    def _group_add_name(
        cache: SpriteSheetCache,
        group: pygame.sprite.Group,
        arr: list[str | None],
        pos: list
    ) -> None:
        """Adds a list of sprites to group.

        Parameters
        ----------
        cache : SpriteSheetCache
            Cache class to get sprite from.
        group : pygame.sprite.Group
            Group to add sprite to.
        arr : list[str  |  None]
            List of cached sprite names to add.
        pos : list
            List of positions for each sprite.

        """
        for x, name in enumerate(arr):
            if not name:
                continue
            group.add(
                StaticSpriteElement.from_pixel(
                    cache.get_static(name),
                    (pos[0] + x) * cache.scale_factor * SUBTILE_SIZE,
                    pos[1] * cache.scale_factor * SUBTILE_SIZE
                )
            )

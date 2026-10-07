from abc import ABC, abstractmethod
import sys
from enum import Enum, auto

import pygame

from ..models import StaticSpriteElement
from ..render import SpriteSheetCache

SUBTILE_SIZE = 8


class LoopState(Enum):
    MAIN_MENU = auto()
    GAME_LOOP = auto()
    DEATH_SCREEN = auto()
    WIN_SCREEN = auto()
    END_GAME = auto()
    SHOW_HIGHSCORE = auto()
    ENTER_HIGHSCORE = auto()


class State(ABC):
    def __init__(self, state):
        self.state = state

    @abstractmethod
    def run(self):
        pass

    def handle_input(self, key_event: pygame.event.Event) -> None:
        match key_event.key:
            case pygame.K_ESCAPE:
                if self.state == LoopState.SHOW_HIGHSCORE:
                    self.state = LoopState.MAIN_MENU
                else:
                    sys.exit()

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

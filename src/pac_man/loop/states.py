from abc import ABC, abstractmethod
import sys
from enum import Enum, auto

import pygame

class LoopState(Enum):
    MAIN_MENU = auto()
    GAME_LOOP = auto()
    DEATH_SCREEN = auto()
    WIN_SCREEN = auto()
    END_GAME = auto()
    HIGHSCORE = auto()

class State(ABC):
    def __init__(self, state):
        self.state = state

    @abstractmethod
    def run(self):
        pass

    def handle_input(self, key_event: pygame.event.Event) -> None:
        match key_event.key:
            case pygame.K_ESCAPE:
                sys.exit()

    def handle_event(self) -> None:
        """handle different types of pygame events"""
        for pygame_event in pygame.event.get():
            if pygame_event.type == pygame.QUIT:
                sys.exit()

            elif pygame_event.type == pygame.KEYDOWN:
                self.handle_input(pygame_event)
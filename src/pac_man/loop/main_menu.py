import sys

import pygame
import logging
from pydantic import ValidationError

from ..render import SpriteSheetCache

from .states import State

SCALE_DIV = 5

class MainMenu(State):
    def __init__(self, screen: pygame.Surface):
        self.screen = screen

        self.scale_factor = min(
            self.screen.get_width() // SCALE_DIV,
            self.screen.get_height() // SCALE_DIV
        )

        try:
            self.asset_cache: SpriteSheetCache = SpriteSheetCache.from_default_file_path(
                scale_factor=self.scale_factor
            )
        except ValidationError as e:
            sys.exit(style="red", markup=False, highlight=False)

            

    def init_draw(self):
        pass

    def render():
        pass

    def run(self):
        pass
from .structures import Tile_Pos
from .spritesheet import SpriteSheetCache
from .tile import TileSpriteFactory, Tile, StaticSpriteElement
from .player import Player
from .text import TextSpriteFactory

import pygame


class Hud:

    def __init__(self,
                 asset_cache: SpriteSheetCache,
                 screen: pygame.Surface) -> None:
        """Create sprites that are needed in level."""
        self.asset_cache = asset_cache
        self.screen = screen

        # NOTE: currently arbitrary
        self.top_display = pygame.Surface((800, 200))
        self.position = pygame.Vector2(0, 50)

        # Text and numbers
        self.text_group = pygame.sprite.Group()

        self.populate_sprite_groups()

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""
        text_factory = TextSpriteFactory(assets=self.asset_cache)

        self.text_group.add(StaticSpriteElement(
            text_factory.from_string(s="high score"),
            x=0,
            y=0
        ))

    def loop(self, dt: float) -> None:
        """Update and display loop to be run every frame.

        Parameters
        ----------
        dt : float
            Delta time used for updating sprites.

        """
        self.top_display.fill((50, 0, 0))

        self.text_group.draw(self.top_display)

        self.screen.blit(self.top_display, self.position)

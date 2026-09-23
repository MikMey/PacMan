from .structures import Tile_Pos
from .spritesheet import SpriteSheetCache
from .tile import SUBTILE_SIZE, StaticSpriteElement
from .player import Player
from .text import TextSpriteFactory

import pygame


class Hud:

    def __init__(self,
                 asset_cache: SpriteSheetCache,
                 screen: pygame.Surface,
                 vertical_padding: int) -> None:
        """Create sprites that are needed in level."""
        self.asset_cache = asset_cache
        self.screen = screen

        # Value Logic
        self.score = 0
        self.high_score = 0

        # Display Logic
        self.top_display = pygame.Surface((
            screen.get_width(),
            vertical_padding
        ))
        self.position = pygame.Vector2(0, 0)

        # Text and numbers
        self.text_group = pygame.sprite.Group()
        self.score_element: StaticSpriteElement
        self.high_score_element: StaticSpriteElement

        self.populate_sprite_groups()

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""
        self.text_factory = TextSpriteFactory(assets=self.asset_cache)

        high_score_surface = self.text_factory.from_string(s="high score")
        self.text_group.add(StaticSpriteElement.from_pixel(
            high_score_surface,
            x=(self.screen.get_width() * 0.75 -
               high_score_surface.get_width() // 2),
            y=0
        ))

        self.high_score_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str(self.high_score)),
            x=(self.screen.get_width() * 0.75 -
               high_score_surface.get_width() // 2),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor
        )
        self.text_group.add(self.high_score_element)

        self.score_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str(self.score)),
            x=(self.screen.get_width() * 0.25),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor
        )
        self.text_group.add(self.score_element)

    def add_score(self, addend: int) -> None:
        """Updates the score and maybe the highscore image.

        Parameters
        ----------
        addend : int
            Number of points to be added to score.

        """
        self.score += addend
        self.score_element.image = self.text_factory.from_string(
            s=str(self.score))

        if self.score > self.high_score:
            self.high_score = self.score
            self.high_score_element.image = self.text_factory.from_string(
                s=str(self.high_score))

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

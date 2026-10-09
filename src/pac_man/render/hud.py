import sys

import pygame
from pydantic import ValidationError

from ..models import SUBTILE_SIZE, StaticSpriteElement

from .spritesheet import SpriteSheetCache
from .text import TextSpriteFactory


class Hud:
    score = 0
    time = -1

    def __init__(self,
                 screen: pygame.Surface,
                 vertical_padding: int,
                 high_score: int,
                 lives: int
                 ) -> None:
        """Create sprites that are needed in level."""
        self.scale_factor = 8
        try:
            self.asset_cache: SpriteSheetCache =\
                SpriteSheetCache.from_default_file_path(
                    scale_factor=self.scale_factor
                )
        except ValidationError as e:
            sys.exit(str(e))
        self.screen = screen
        self.vertical_padding = vertical_padding

        # Value Logic
        # self.score = 0
        self.high_score = high_score
        self.lives = lives

        # Display Logic
        self.top_display = pygame.Surface((
            screen.get_width(), vertical_padding
        ))
        self.top_position = pygame.Vector2(
            0, 0
        )

        self.bottom_display = pygame.Surface((
            screen.get_width(), vertical_padding
        ))
        self.bottom_position = pygame.Vector2(
            0, screen.get_height() - vertical_padding
        )

        # self.time = -1
        self.time_delta: float = 0

        # Text and numbers
        self.score_element: StaticSpriteElement
        self.high_score_element: StaticSpriteElement
        self.text_group: pygame.sprite.Group = pygame.sprite.Group()
        self.lives_group: pygame.sprite.Group = pygame.sprite.Group()
        self.timer_group: pygame.sprite.Group = pygame.sprite.Group()

        self.populate_sprite_groups()

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""
        self.text_group = pygame.sprite.Group()
        self.lives_group = pygame.sprite.Group()
        self.timer_group = pygame.sprite.Group()

        self.text_factory = TextSpriteFactory(assets=self.asset_cache)

        # Top Display
        self.level_name_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str("level -1")),
            x=(self.screen.get_width() * 0.5),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor / 2
        )
        self.text_group.add(self.level_name_element)

        self.score_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str(self.score)),
            x=(self.screen.get_width() * 0.25),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor * 1.5
        )
        self.text_group.add(self.score_element)

        high_score_surface = self.text_factory.from_string(s="high score")
        self.text_group.add(StaticSpriteElement.from_pixel(
            high_score_surface,
            x=(self.screen.get_width() * 0.75 -
               high_score_surface.get_width() // 2),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor / 2
        ))

        self.high_score_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str(self.high_score)),
            x=(self.screen.get_width() * 0.75 -
               high_score_surface.get_width() // 6),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor * 1.5
        )
        self.text_group.add(self.high_score_element)

        # Bottom Display
        self.update_lives(self.lives)

        static_timer_element = self.text_factory.from_string(s="timer")
        self.timer_group.add(StaticSpriteElement.from_pixel(
            static_timer_element,
            x=(self.screen.get_width() * 0.75 -
               static_timer_element.get_width() // 2),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor / 2
        ))

        self.time_element = StaticSpriteElement.from_pixel(
            self.text_factory.from_string(s=str(self.time)),
            x=(self.screen.get_width() * 0.75 -
               static_timer_element.get_width() // 6),
            y=SUBTILE_SIZE * self.asset_cache._text_scale_factor * 1.5
        )
        self.timer_group.add(self.time_element)

    def update_lives(self, new_lives: int) -> None:
        self.lives = new_lives

        live_sprite = self.asset_cache.get_anim("PACMAN-LEFT")[3]
        self.lives_group.empty()

        for i in range(self.lives):
            self.lives_group.add(StaticSpriteElement.from_pixel(
                live_sprite,
                x=(self.vertical_padding / 2 -
                    live_sprite.get_height() / 2 +
                    i * live_sprite.get_height()),
                y=(self.vertical_padding / 2 -
                    live_sprite.get_height() / 2)
            ))

    def update_time_second(self) -> bool:

        self.time -= 1
        if self.time < 0:
            return True

        self.time_element.image = self.text_factory.from_string(
                    s=str(self.time))
        return False

    def update_level_name(self, new_name: str) -> None:
        self.level_name_element.image = self.text_factory.from_string(
            s=new_name)

    def add_score(self) -> None:
        """Updates the score and maybe the highscore image.

        Parameters
        ----------
        addend : int
            Number of points to be added to score.

        """
        self.score_element.image = self.text_factory.from_string(
            s=str(Hud.score))

        if Hud.score > self.high_score:
            self.high_score = Hud.score
            self.high_score_element.image = self.text_factory.from_string(
                s=str(self.high_score))

    def render(self) -> None:
        # self.top_display.fill((50, 0, 0))
        self.top_display.fill(0)
        self.text_group.draw(self.top_display)
        self.screen.blit(self.top_display, self.top_position)

        # self.bottom_display.fill((120, 0, 43))
        self.bottom_display.fill(0)
        self.lives_group.draw(self.bottom_display)
        self.timer_group.draw(self.bottom_display)
        self.screen.blit(self.bottom_display, self.bottom_position)

    def loop(self, dt: float) -> bool:
        """Update and display loop to be run every frame.

        Parameters
        ----------
        dt : float
            Delta time used for updating sprites.

        """
        self.time_delta += dt
        while self.time_delta >= 1:
            if self.update_time_second():
                return True

            self.time_delta -= 1
        self.add_score()
        self.render()
        return False

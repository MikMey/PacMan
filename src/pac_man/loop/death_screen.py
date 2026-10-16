from typing import Optional
import functools
import pygame

# from ..render.spritesheet import SpriteSheetCache
from .highscore import _BaseHighscore
from .states import State, LoopState


class DeathScreen(_BaseHighscore, State):
    """Shows up after running out of lives."""

    def __init__(self,
                 highscore_file: Optional[str],
                 screen: Optional[pygame.Surface]):
        """Initializes and prepares sprites."""
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)
        self._prep_sprites_enter()

    def _prep_sprites_enter(self) -> None:
        """Prepares sprites."""
        self._guide: pygame.sprite.Group = pygame.sprite.Group()

        prep = functools.partial(
            self._group_add_str,
            self.asset_cache,
            self._guide
        )

        prep("YOU LOST", [6, 2])
        prep("any key to continue", [0, 4])

    def handle_input(self, key_event: pygame.event.Event) -> None:
        """Returns to main menu when called."""
        self.state = LoopState.ENTER_HIGHSCORE

    def run(self) -> LoopState:
        """Draws sprites and waits for any input to return to menu."""
        self.state = LoopState.DEATH_SCREEN
        self._guide.draw(self.surface)
        self.screen.blit(self.surface, self.position)
        self.handle_event()
        return self.state

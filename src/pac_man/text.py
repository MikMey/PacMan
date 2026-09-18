from .spritesheet import SpriteSheetCache

from pydantic import BaseModel, PrivateAttr, ConfigDict
from typing import Any
import pygame


DEFAULT_CHAR_SIZE = 8


class TextSpriteFactory(BaseModel):
    """Bakes text into one surface (separated for performance).

    Parameters
    ----------
    assets : :obj:`SpriteSheetCache`
        Cached assets to be used in creating tiles.

    """
    assets: SpriteSheetCache

    _sub_w: int = PrivateAttr()
    _sub_h: int = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set subtile width and height."""
        super().__init__(*args, **kwargs)

        sub_sample = self.assets.get_static("CHAR-0")
        self._sub_w = sub_sample.get_width()
        self._sub_h = sub_sample.get_height()

    def from_string(self, s: str) -> pygame.Surface:
        """Get baked text surface from string.

        Parameters
        ----------
        s : str
            Tile to get the surface data of.

        Returns
        -------
        pygame.Surface
            Ready to draw surface of collected letters.

        """
        s = s.upper()

        lines_count = len(s.split('\n'))
        max_width = max([len(ln) for ln in s.split('\n')])
        surface = pygame.Surface((self._sub_w * max_width,
                                  self._sub_h * lines_count))

        def at(w: int, h: int) -> tuple[int, int]:
            """Helper to convert subtile positions to pixel positions."""
            return (self._sub_w * w, self._sub_h * h)

        for line_idx, line in enumerate(s.split('\n')):
            for c_idx, c in enumerate(line):
                if c.isspace():
                    continue
                try:
                    c_surface = self.assets.get_static(f"CHAR-{c}")
                except KeyError:
                    c_surface = self.assets.get_static("CHAR-COPYRIGHT")

                surface.blit(c_surface, at(c_idx, line_idx))

        return surface
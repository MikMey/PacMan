from typing import Any, Optional, ClassVar
from dataclasses import dataclass

from pydantic import BaseModel, PrivateAttr, ConfigDict
import pygame

from ..utils import Tile_Pos
from ..render import SpriteSheetCache


SUBTILE_SIZE = 8
TILE_SIZE = SUBTILE_SIZE * 3


@dataclass
class Tile:
    """Metadata of tile walls and items (not holding sprite data).

    Parameters
    ----------
    is_top_closed : bool
        True if there is a wall to the north of tile.
    is_right_closed : bool
        True if there is a wall to the east of tile.
    is_bottom_closed : bool
        True if there is a wall to the south of tile.
    is_left_closed : bool
        True if there is a wall to the west of tile.

    """
    # for sprite
    is_top_closed: bool
    is_right_closed: bool
    is_bottom_closed: bool
    is_left_closed: bool

    # for movement
    x: int
    y: int

    top: "Optional[Tile]" = None
    right: "Optional[Tile]" = None
    left: "Optional[Tile]" = None
    bottom: "Optional[Tile]" = None

    neighbours: Optional[list["Tile"]] = None

    cost: Optional[int] = -1

    _matrix: ClassVar[list[list["Tile"]]] = []

    def create_reference(self) -> None:
        """reference neighbouring tiles for
        easy access in rendering and ghost ai"""

        if self.y > 0:
            self.top = Tile._matrix[self.y - 1][self.x]
        if len(Tile._matrix) - 1 > self.y:
            self.bottom = Tile._matrix[self.y + 1][self.x]
        if self.x > 0:
            self.left = Tile._matrix[self.y][self.x - 1]
        if len(Tile._matrix[0]) - 1 > self.x:
            self.right = Tile._matrix[self.y][self.x + 1]

        temp = []

        if not self.is_top_closed:
            temp.append(self.top)
        if not self.is_bottom_closed:
            temp.append(self.bottom)
        if not self.is_left_closed:
            temp.append(self.left)
        if not self.is_right_closed:
            temp.append(self.right)

        self.neighbours = temp

    @classmethod
    def create(cls, value: int, x: int, y: int) -> "Tile":
        """Converts MazeGenerator hex values to class flags.

        Parameters
        ----------
        value : int
            Hex value to be converted.

        """
        return cls(
            x=x,
            y=y,
            is_top_closed=bool(value & 0b0001),
            is_right_closed=bool(value & 0b0010),
            is_bottom_closed=bool(value & 0b0100),
            is_left_closed=bool(value & 0b1000),
        )

    def set_matrix(matrix: list[list["Tile"]]) -> None:
        Tile._matrix = matrix

    def get_tile(pos: Tile_Pos) -> "Tile":
        tile: Tile = Tile._matrix[pos.y][pos.x]
        return tile


class TileSpriteFactory(BaseModel):
    """Creates tiles from tile data (separated for performance).

    Parameters
    ----------
    assets : :obj:`SpriteSheetCache`
        Cached assets to be used in creating tiles

    """
    assets: SpriteSheetCache

    _sub_w: int = PrivateAttr()
    _sub_h: int = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Set subtile width and height."""
        # NOTE: Currently kinda ugly
        super().__init__(*args, **kwargs)

        sub_sample = self.assets.get_static("WALL-RIGHT")
        self._sub_w = sub_sample.get_width()
        self._sub_h = sub_sample.get_height()

    def from_tile(
            self,
            tile: Tile
            ) -> pygame.Surface:
        """Get baked tile surface from tile data and its neighbors.

        Parameters
        ----------
        tile : Tile
            Tile to get the surface data of.
        tile.top : Optional[Tile]
            Tile to the north of the main tile.
        tile.right : Optional[Tile]
            Tile to the east of the main tile.
        tile.bottom : Optional[Tile]
            Tile to the south of the main tile.
        tile.left : Optional[Tile]
            Tile to the west of the main tile.

        Returns
        -------
        pygame.Surface
            Ready to draw surface of collected subtiles.

        """
        surface = pygame.Surface((self._sub_w * 3, self._sub_h * 3))

        def blit(name: str, w: int, h: int) -> None:
            """Helper function to blit to surface from subtile position.

            Parameters
            ----------
            name : str
                Key of static surface in :obj:`SpriteSheetCache`.
            w : int
                Horizontal subtile position (0, 1, 2).
            h : int
                Vertical subtile position (0, 1, 2).

            """
            surface.blit(
                self.assets.get_static(name),
                (self._sub_w * w, self._sub_h * h)
            )

        # Wall Ends (Corners)
        if tile.top is not None:
            if not tile.is_right_closed and tile.top.is_right_closed:
                blit("CORNER-TOP-RIGHT", 2, 0)
            if not tile.is_left_closed and tile.top.is_left_closed:
                blit("CORNER-TOP-LEFT", 0, 0)
        if tile.right is not None:
            if not tile.is_top_closed and tile.right.is_top_closed:
                blit("CORNER-TOP-RIGHT", 2, 0)
            if not tile.is_bottom_closed and tile.right.is_bottom_closed:
                blit("CORNER-BOTTOM-RIGHT", 2, 2)
        if tile.bottom is not None:
            if not tile.is_right_closed and tile.bottom.is_right_closed:
                blit("CORNER-BOTTOM-RIGHT", 2, 2)
            if not tile.is_left_closed and tile.bottom.is_left_closed:
                blit("CORNER-BOTTOM-LEFT", 0, 2)
        if tile.left is not None:
            if not tile.is_top_closed and tile.left.is_top_closed:
                blit("CORNER-TOP-LEFT", 0, 0)
            if not tile.is_bottom_closed and tile.left.is_bottom_closed:
                blit("CORNER-BOTTOM-LEFT", 0, 2)

        # Main Wall and Border Tilings
        if tile.is_top_closed:
            if tile.top is None:
                for i in range(3):
                    blit("BORDER-TOP", i, 0)
            else:
                for i in range(3):
                    blit("WALL-TOP", i, 0)
            pass
        if tile.is_right_closed:
            if tile.right is None:
                for i in range(3):
                    blit("BORDER-RIGHT", 2, i)
            else:
                for i in range(3):
                    blit("WALL-RIGHT", 2, i)
        if tile.is_bottom_closed:
            if tile.bottom is None:
                for i in range(3):
                    blit("BORDER-BOTTOM", i, 2)
            else:
                for i in range(3):
                    blit("WALL-BOTTOM", i, 2)
        if tile.is_left_closed:
            if tile.left is None:
                for i in range(3):
                    blit("BORDER-LEFT", 0, i)
            else:
                for i in range(3):
                    blit("WALL-LEFT", 0, i)

        # Border to Wall Connections
        if tile.is_top_closed and tile.top is None:
            if tile.is_right_closed:
                blit("BORDER-TOP-WALL-RIGHT", 2, 0)
            if tile.is_left_closed:
                blit("BORDER-TOP-WALL-LEFT", 0, 0)
        if tile.is_right_closed and tile.right is None:
            if tile.is_bottom_closed:
                blit("BORDER-RIGHT-WALL-BOTTOM", 2, 2)
            if tile.is_top_closed:
                blit("BORDER-RIGHT-WALL-TOP", 2, 0)
        if tile.is_bottom_closed and tile.bottom is None:
            if tile.is_right_closed:
                blit("BORDER-BOTTOM-WALL-RIGHT", 2, 2)
            if tile.is_left_closed:
                blit("BORDER-BOTTOM-WALL-LEFT", 0, 2)
        if tile.is_left_closed and tile.left is None:
            if tile.is_bottom_closed:
                blit("BORDER-LEFT-WALL-BOTTOM", 0, 2)
            if tile.is_top_closed:
                blit("BORDER-LEFT-WALL-TOP", 0, 0)

        # Border Corners
        if tile.top is None and tile.right is None:
            blit("BORDER-TOP-RIGHT", 2, 0)
        if tile.top is None and tile.left is None:
            blit("BORDER-TOP-LEFT", 0, 0)
        if tile.bottom is None and tile.right is None:
            blit("BORDER-BOTTOM-RIGHT", 2, 2)
        if tile.bottom is None and tile.left is None:
            blit("BORDER-BOTTOM-LEFT", 0, 2)

        # End all Borders early
        if (tile.top is None or tile.right is None or
                tile.bottom is None or tile.left is None):
            return surface

        # Wall Conenctions
        if tile.is_top_closed and tile.is_right_closed:
            blit("WALL-TOP-RIGHT", 2, 0)
        if tile.is_top_closed and tile.is_left_closed:
            blit("WALL-TOP-LEFT", 0, 0)
        if tile.is_bottom_closed and tile.is_right_closed:
            blit("WALL-BOTTOM-RIGHT", 2, 2)
        if tile.is_bottom_closed and tile.is_left_closed:
            blit("WALL-BOTTOM-LEFT", 0, 2)

        return surface

    def get_item(self, name: str) -> pygame.Surface:
        """Get item of tile based on tile data.

        Parameters
        ----------
        name : str
            Name of the item to get.

        Returns
        -------
        pygame.Surface
            Surface of the item (e.g. pacgum)
        """
        surface = pygame.Surface((self._sub_w, self._sub_h))

        match name:
            case "pacgum":
                surface.blit(self.assets.get_static("PACGUM"), (0, 0))
            case "super_pacgum":
                surface.blit(self.assets.get_static("SUPER-PACGUM"), (0, 0))

        return surface


class StaticSpriteElement(pygame.sprite.Sprite):
    """Sprite of background elements that are not animated.

    Parameters
    ----------
    image : pygame.Surface
        Image to be drawn on screen.
    x : float
        On screen posiition (times its on width).
    y : float
        On screen posiition (times its on height).

    """
    image: pygame.Surface
    rect = pygame.Rect

    def __init__(self, image: pygame.Surface, rect: pygame.Rect) -> None:
        """Setting up pydantic sprite attributes."""
        super().__init__()

        self.image = image
        self.rect = rect

    @classmethod
    def from_pixel(cls, image: pygame.Surface,
                   x: float, y: float) -> "StaticSpriteElement":
        """_summary_

        Parameters
        ----------
        surface : pygame.Surface
            _description_
        x : float
            _description_
        y : float
            _description_

        """
        return cls(image=image, rect=image.get_rect(topleft=(x, y)))

    @classmethod
    def from_relative(cls, image: pygame.Surface,
                      x: float, y: float) -> "StaticSpriteElement":

        return cls(image=image, rect=image.get_rect(topleft=(
            x * image.get_width(),
            y * image.get_height()
        )))

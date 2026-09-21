from .spritesheet import SpriteSheetCache

from pydantic import BaseModel, PrivateAttr, ConfigDict
from typing import Any, Optional
import pygame


SUBTILE_SIZE = 8
TILE_SIZE = SUBTILE_SIZE * 3


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
            self, main_tile: Tile,
            top_tile: Optional[Tile], right_tile: Optional[Tile],
            bottom_tile: Optional[Tile], left_tile: Optional[Tile]
            ) -> pygame.Surface:
        """Get baked tile surface from tile data and its neighbors.

        Parameters
        ----------
        main_tile : Tile
            Tile to get the surface data of.
        top_tile : Optional[Tile]
            Tile to the north of the main tile.
        right_tile : Optional[Tile]
            Tile to the east of the main tile.
        bottom_tile : Optional[Tile]
            Tile to the south of the main tile.
        left_tile : Optional[Tile]
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
        if top_tile is not None:
            if not main_tile.is_right_closed and top_tile.is_right_closed:
                blit("CORNER-TOP-RIGHT", 2, 0)
            if not main_tile.is_left_closed and top_tile.is_left_closed:
                blit("CORNER-TOP-LEFT", 0, 0)
        if right_tile is not None:
            if not main_tile.is_top_closed and right_tile.is_top_closed:
                blit("CORNER-TOP-RIGHT", 2, 0)
            if not main_tile.is_bottom_closed and right_tile.is_bottom_closed:
                blit("CORNER-BOTTOM-RIGHT", 2, 2)
        if bottom_tile is not None:
            if not main_tile.is_right_closed and bottom_tile.is_right_closed:
                blit("CORNER-BOTTOM-RIGHT", 2, 2)
            if not main_tile.is_left_closed and bottom_tile.is_left_closed:
                blit("CORNER-BOTTOM-LEFT", 0, 2)
        if left_tile is not None:
            if not main_tile.is_top_closed and left_tile.is_top_closed:
                blit("CORNER-TOP-LEFT", 0, 0)
            if not main_tile.is_bottom_closed and left_tile.is_bottom_closed:
                blit("CORNER-BOTTOM-LEFT", 0, 2)

        # Main Wall and Border Tilings
        if main_tile.is_top_closed:
            if top_tile is None:
                for i in range(3):
                    blit("BORDER-TOP", i, 0)
            else:
                for i in range(3):
                    blit("WALL-TOP", i, 0)
            pass
        if main_tile.is_right_closed:
            if right_tile is None:
                for i in range(3):
                    blit("BORDER-RIGHT", 2, i)
            else:
                for i in range(3):
                    blit("WALL-RIGHT", 2, i)
        if main_tile.is_bottom_closed:
            if bottom_tile is None:
                for i in range(3):
                    blit("BORDER-BOTTOM", i, 2)
            else:
                for i in range(3):
                    blit("WALL-BOTTOM", i, 2)
        if main_tile.is_left_closed:
            if left_tile is None:
                for i in range(3):
                    blit("BORDER-LEFT", 0, i)
            else:
                for i in range(3):
                    blit("WALL-LEFT", 0, i)

        # Border to Wall Connections
        if main_tile.is_top_closed and top_tile is None:
            if main_tile.is_right_closed:
                blit("BORDER-TOP-WALL-RIGHT", 2, 0)
            if main_tile.is_left_closed:
                blit("BORDER-TOP-WALL-LEFT", 0, 0)
        if main_tile.is_right_closed and right_tile is None:
            if main_tile.is_bottom_closed:
                blit("BORDER-RIGHT-WALL-BOTTOM", 2, 2)
            if main_tile.is_top_closed:
                blit("BORDER-RIGHT-WALL-TOP", 2, 0)
        if main_tile.is_bottom_closed and bottom_tile is None:
            if main_tile.is_right_closed:
                blit("BORDER-BOTTOM-WALL-RIGHT", 2, 2)
            if main_tile.is_left_closed:
                blit("BORDER-BOTTOM-WALL-LEFT", 0, 2)
        if main_tile.is_left_closed and left_tile is None:
            if main_tile.is_bottom_closed:
                blit("BORDER-LEFT-WALL-BOTTOM", 0, 2)
            if main_tile.is_top_closed:
                blit("BORDER-LEFT-WALL-TOP", 0, 0)

        # Border Corners
        if top_tile is None and right_tile is None:
            blit("BORDER-TOP-RIGHT", 2, 0)
        if top_tile is None and left_tile is None:
            blit("BORDER-TOP-LEFT", 0, 0)
        if bottom_tile is None and right_tile is None:
            blit("BORDER-BOTTOM-RIGHT", 2, 2)
        if bottom_tile is None and left_tile is None:
            blit("BORDER-BOTTOM-LEFT", 0, 2)

        # End all Borders early
        if (top_tile is None or right_tile is None or
                bottom_tile is None or left_tile is None):
            return surface

        # Wall Conenctions
        if main_tile.is_top_closed and main_tile.is_right_closed:
            blit("WALL-TOP-RIGHT", 2, 0)
        if main_tile.is_top_closed and main_tile.is_left_closed:
            blit("WALL-TOP-LEFT", 0, 0)
        if main_tile.is_bottom_closed and main_tile.is_right_closed:
            blit("WALL-BOTTOM-RIGHT", 2, 2)
        if main_tile.is_bottom_closed and main_tile.is_left_closed:
            blit("WALL-BOTTOM-LEFT", 0, 2)

        return surface

    def get_item(self, tile: Tile) -> pygame.Surface:
        """Get item of tile based on tile data.

        Parameters
        ----------
        tile : Tile
            Tile to get the item of.

        Returns
        -------
        pygame.Surface
            Surface of the item (e.g. pacgum)
        """
        # NOTE: not fully implemented
        surface = pygame.Surface((self._sub_w, self._sub_h))

        surface.blit(self.assets.get_static("PACGUM"), (0, 0))

        return surface


class StaticSpriteElement(pygame.sprite.Sprite):
    """Sprite of background elements that are not animated.

    Parameters
    ----------
    image : pygame.Surface
        Image to be drawn on screen.
    x : int
        On screen posiition (times its on width).
    y : int
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
                   x: int, y: int) -> "StaticSpriteElement":
        """_summary_

        Parameters
        ----------
        surface : pygame.Surface
            _description_
        x : int
            _description_
        y : int
            _description_

        """
        return cls(image=image, rect=image.get_rect(topleft=(x, y)))

    @classmethod
    def from_relative(cls, image: pygame.Surface,
                      x: int, y: int) -> "StaticSpriteElement":

        return cls(image=image, rect=image.get_rect(topleft=(
            x * image.get_width(),
            y * image.get_height()
        )))


class Tile(BaseModel):
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
    is_top_closed: bool
    is_right_closed: bool
    is_bottom_closed: bool
    is_left_closed: bool

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_hex_state(cls, hex: int) -> "Tile":
        """Converts MazeGenerator hex values to class flags.

        Parameters
        ----------
        hex : int
            Hex value to be converted.

        """
        return cls(
            is_top_closed=bool(hex & 0b0001),
            is_right_closed=bool(hex & 0b0010),
            is_bottom_closed=bool(hex & 0b0100),
            is_left_closed=bool(hex & 0b1000),
        )

# SUBTILE_SIZE = 8


# class Tile(BaseModel):

#     closed_state: int = Field(ge=0, lt=16)
#     screen: ScreenBuffer

#     def is_dir_walled(self, direction: str) -> bool:

#         dir = direction.lower()[0]

#         match dir:
#             case 'n' | 't':
#                 return bool(self.closed_state & 0b0001)
#             case 'e' | 'r':
#                 return bool(self.closed_state & 0b0010)
#             case 's' | 'b':
#                 return bool(self.closed_state & 0b0100)
#             case 'w' | 'l':
#                 return bool(self.closed_state & 0b1000)
#             case _:
#                 raise ValueError(f"Direction {direction!r} not recognized")

#     def display(self, pos: Position, scale: int = 6) -> None:

#         self.screen.draw("VOID", Position(
#             pos.x + 0 * scale * SUBTILE_SIZE,
#             pos.y + 0 * scale * SUBTILE_SIZE), scale)
#         to_draw = "VOID"
#         if self.is_dir_walled("top"):
#             to_draw = "B-T"
#         self.screen.draw(to_draw, Position(
#             pos.x + 1 * scale * SUBTILE_SIZE,
#             pos.x + 0 * scale * SUBTILE_SIZE), scale)
#         self.screen.draw("VOID", Position(
#             pos.x + 2 * scale * SUBTILE_SIZE,
#             pos.x + 0 * scale * SUBTILE_SIZE), scale)

#         to_draw = "VOID"
#         if self.is_dir_walled("lft"):
#             to_draw = "B-L"
#         self.screen.draw(to_draw, Position(
#             pos.x + 0 * scale * SUBTILE_SIZE,
#             pos.x + 1 * scale * SUBTILE_SIZE), scale)
#         self.screen.draw("VOID", Position(
#             pos.x + 1 * scale * SUBTILE_SIZE,
#             pos.x + 1 * scale * SUBTILE_SIZE), scale)
#         to_draw = "VOID"
#         if self.is_dir_walled("rgt"):
#             to_draw = "B-R"
#         self.screen.draw(to_draw, Position(
#             pos.x + 2 * scale * SUBTILE_SIZE,
#             pos.x + 1 * scale * SUBTILE_SIZE), scale)

#         self.screen.draw("VOID", Position(
#             pos.x + 0 * scale * SUBTILE_SIZE,
#             pos.x + 2 * scale * SUBTILE_SIZE), scale)
#         to_draw = "VOID"
#         if self.is_dir_walled("btm"):
#             to_draw = "B-B"
#         self.screen.draw(to_draw, Position(
#             pos.x + 1 * scale * SUBTILE_SIZE,
#             pos.x + 2 * scale * SUBTILE_SIZE), scale)
#         self.screen.draw("VOID", Position(
#             pos.x + 2 * scale * SUBTILE_SIZE,
#             pos.x + 2 * scale * SUBTILE_SIZE), scale)

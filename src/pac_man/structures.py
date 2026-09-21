from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(slots=True)
class Pixel_Pos:
    """Pixel position of spritesheet or screen.

    Attributes
    ----------
    x : int
        Horizontal pixel position.
    y : int
        Vertical pixel position.

    """
    x: int
    y: int

    def __iter__(self):
        """Defines attribute order."""
        yield self.x
        yield self.y


@dataclass(slots=True)
class Tile_Pos:
    """Tile position of game.

    Attributes
    ----------
    x : int
        Horizontal tile position.
    y : int
        Vertical tile position.

    """
    x: int
    y: int

    def to_pixel_pos(self, tile_size: int) -> Pixel_Pos:
        """Returns new instance of multiplied Position."""
        return Pixel_Pos(self.x * tile_size, self.y * tile_size)

    def __iter__(self):
        """Defines attribute order."""
        yield self.x
        yield self.y

# UNUSED
# @dataclass(slots=True)
# class Size:
#     """Pixel size of a sprite or surface.

#     Attributes
#     ----------
#     width : int
#         Horizontal pixel size.
#     height : int
#         Vertical pixel size.

#     """
#     width: int = Field(ge=0)
#     height: int = Field(ge=0)

#     def __iter__(self):
#         """Defines attribute order."""
#         yield self.width
#         yield self.height


@dataclass(slots=True)
class Direction:
    """Negative Identity matrix for movement on tiles.

    Attributes
    ----------
    hori : int
        Movement on the X-Axis (-1, 0, 1).
    vert : int
        Movement on the Y-Axis (-1, 0, 1).

    """
    hori: int = Field(ge=-1, le=1, default=0)
    vert: int = Field(ge=-1, le=1, default=0)

    def set(self, hori: int, vert: int) -> None:
        """Sets new direction."""
        self.hori = hori
        self.vert = vert

    def is_still(self) -> bool:
        """True if hori and vert are zero, False otherwise."""
        return self.hori == 0 and self.vert == 0

    def __iter__(self):
        """Defines attribute order."""
        yield self.hori
        yield self.vert

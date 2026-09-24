
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
    x: int = Field(default=0)
    y: int = Field(default=0)

    def to_pixel_pos(self, tile_size: int) -> Pixel_Pos:
        """Returns new instance of multiplied Position."""
        return Pixel_Pos(self.x * tile_size, self.y * tile_size)

    def __iter__(self):
        """Defines attribute order."""
        yield self.x
        yield self.y

    def set(self, pos: tuple):
        self.x = pos[0]
        self.y = pos[1]

    def get(self) -> tuple:
        return (self.x, self.y)

    def add(self, change: Tile_Pos | UnitVector):
        self.x += change.x
        self.y += change.y

    def copy(self) -> Tile_Pos:
        new_tile: Tile_Pos = Tile_Pos()
        new_tile.set(self.get())
        return(new_tile)

    @staticmethod
    def get_neighbour(tile: Tile_Pos, unit_vector: UnitVector) -> Tile_Pos:
        new_tile: Tile_Pos = tile.copy()
        new_tile.add(unit_vector)
        return new_tile


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
class UnitVector:
    """Negative Identity matrix for movement on tiles.

    Attributes
    ----------
    x : int
        Movement on the X-Axis (-1, 0, 1).
    y : int
        Movement on the Y-Axis (-1, 0, 1).

    """
    x: int = Field(ge=-1, le=1, default=0)
    y: int = Field(ge=-1, le=1, default=0)

    def set(self, direction: tuple = (0, 0))-> None:
        """Sets new direction."""
        if not direction:
            raise ValueError("'direction' attr is None")
        self.x = direction[0]
        self.y = direction[1]

    def get(self) -> tuple:
        return (self.x, self.y)

    def is_still(self) -> bool:
        """True if hori and vert are zero, False otherwise."""
        return self.x == 0 and self.y == 0

    def __iter__(self):
        """Defines attribute order."""
        yield self.x
        yield self.y

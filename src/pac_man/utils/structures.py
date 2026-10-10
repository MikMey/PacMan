from typing import Any, Generator
from pydantic import Field
from pydantic.dataclasses import dataclass


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

    def set(self, direction: tuple[int, int] = (0, 0)) -> None:
        """Sets new direction."""
        if not direction:
            raise ValueError("'direction' attr is None")
        self.x = direction[0]
        self.y = direction[1]

    def get(self) -> tuple[int, int]:
        """Returns a tuple of x and y direction."""
        return (self.x, self.y)

    def is_still(self) -> bool:
        """True if hori and vert are zero, False otherwise."""
        return self.x == 0 and self.y == 0

    def __iter__(self) -> Generator[Any, Any, Any]:
        """Defines attribute order."""
        yield self.x
        yield self.y


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

    def __iter__(self) -> Generator[Any, Any, Any]:
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

    def __iter__(self) -> Generator[Any, Any, Any]:
        """Defines attribute order."""
        yield self.x
        yield self.y

    def set(self, pos: tuple[int, int]) -> None:
        """Sets ints of tuple to x and y attributes."""
        self.x = pos[0]
        self.y = pos[1]

    def get(self) -> tuple[int, int]:
        """Returns a tuple of x and y position."""
        return (self.x, self.y)

    def add(self, change: "Tile_Pos | UnitVector") -> None:
        """Adds position/direction class attributes to own."""
        self.x += change.x
        self.y += change.y

    def copy(self) -> "Tile_Pos":
        """Returns a copy of the current class."""
        new_tile: Tile_Pos = Tile_Pos()
        new_tile.set(self.get())
        return (new_tile)

    @staticmethod
    def get_neighbour(tile: "Tile_Pos", unit_vector: UnitVector) -> "Tile_Pos":
        """Returns a new Tile_Pos class with unit_vector offset.

        Parameters
        ----------
        tile : Tile_Pos
            Starting tile.
        unit_vector : UnitVector
            Direction offset of new tile.

        Returns
        -------
        Tile_Pos
            Tile after unit_vector operation.

        """
        new_tile: Tile_Pos = tile.copy()
        new_tile.add(unit_vector)
        return new_tile

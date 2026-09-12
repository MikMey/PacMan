from .structures import Position
from .screenbuffer import ScreenBuffer
from .tile import Tile

from pydantic import BaseModel, PrivateAttr


SUBTILE_SIZE = 8

# Painfully slow idk why


class Game(BaseModel):

    closed_data: list[list[int]]
    screen: ScreenBuffer

    _tile_map: list[list[Tile]] = PrivateAttr(default_factory=list)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        for row in self.closed_data:
            new_row = []

            for item in row:
                new_row.append(Tile(closed_state=item, screen=self.screen))

            self._tile_map.append(new_row)

    def display(self) -> None:
        self._tile_map[0][0].display(pos=Position(0, 0), scale=6)

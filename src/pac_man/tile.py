from .structures import Position
from .screenbuffer import ScreenBuffer

from pydantic import BaseModel, Field


SUBTILE_SIZE = 8


class Tile(BaseModel):

    closed_state: int = Field(ge=0, lt=16)
    screen: ScreenBuffer

    def is_dir_walled(self, direction: str) -> bool:

        dir = direction.lower()[0]

        match dir:
            case 'n' | 't':
                return bool(self.closed_state & 0b0001)
            case 'e' | 'r':
                return bool(self.closed_state & 0b0010)
            case 's' | 'b':
                return bool(self.closed_state & 0b0100)
            case 'w' | 'l':
                return bool(self.closed_state & 0b1000)
            case _:
                raise ValueError(f"Direction {direction!r} not recognized")

    def display(self, pos: Position, scale: int = 6) -> None:

        self.screen.draw("VOID", Position(
            pos.x + 0 * scale * SUBTILE_SIZE,
            pos.y + 0 * scale * SUBTILE_SIZE), scale)
        to_draw = "VOID"
        if self.is_dir_walled("top"):
            to_draw = "B-T"
        self.screen.draw(to_draw, Position(
            pos.x + 1 * scale * SUBTILE_SIZE,
            pos.x + 0 * scale * SUBTILE_SIZE), scale)
        self.screen.draw("VOID", Position(
            pos.x + 2 * scale * SUBTILE_SIZE,
            pos.x + 0 * scale * SUBTILE_SIZE), scale)

        to_draw = "VOID"
        if self.is_dir_walled("lft"):
            to_draw = "B-L"
        self.screen.draw(to_draw, Position(
            pos.x + 0 * scale * SUBTILE_SIZE,
            pos.x + 1 * scale * SUBTILE_SIZE), scale)
        self.screen.draw("VOID", Position(
            pos.x + 1 * scale * SUBTILE_SIZE,
            pos.x + 1 * scale * SUBTILE_SIZE), scale)
        to_draw = "VOID"
        if self.is_dir_walled("rgt"):
            to_draw = "B-R"
        self.screen.draw(to_draw, Position(
            pos.x + 2 * scale * SUBTILE_SIZE,
            pos.x + 1 * scale * SUBTILE_SIZE), scale)

        self.screen.draw("VOID", Position(
            pos.x + 0 * scale * SUBTILE_SIZE,
            pos.x + 2 * scale * SUBTILE_SIZE), scale)
        to_draw = "VOID"
        if self.is_dir_walled("btm"):
            to_draw = "B-B"
        self.screen.draw(to_draw, Position(
            pos.x + 1 * scale * SUBTILE_SIZE,
            pos.x + 2 * scale * SUBTILE_SIZE), scale)
        self.screen.draw("VOID", Position(
            pos.x + 2 * scale * SUBTILE_SIZE,
            pos.x + 2 * scale * SUBTILE_SIZE), scale)

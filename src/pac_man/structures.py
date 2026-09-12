from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(slots=True)
class Position:
    x: int = Field(ge=0)
    y: int = Field(ge=0)

    def __iter__(self):
        yield self.x
        yield self.y


@dataclass(slots=True)
class Size:
    width: int = Field(ge=0)
    height: int = Field(ge=0)

    def __iter__(self):
        yield self.width
        yield self.height

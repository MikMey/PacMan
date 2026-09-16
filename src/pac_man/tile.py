from .spritesheet import SpriteSheetCache

from pydantic import BaseModel, PrivateAttr, ConfigDict
from typing import Any, Optional
import pygame


class TileSpriteFactory(BaseModel):

    assets: SpriteSheetCache

    _sub_w: int = PrivateAttr()
    _sub_h: int = PrivateAttr()

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:

        super().__init__(*args, **kwargs)

        sub_sample = self.assets.get_static("WALL-FULL")
        self._sub_w = sub_sample.get_width()
        self._sub_h = sub_sample.get_height()

    def from_tile(
            self, main_tile: Tile,
            top_tile: Optional[Tile], right_tile: Optional[Tile],
            bottom_tile: Optional[Tile], left_tile: Optional[Tile]
            ) -> pygame.Surface:

        surface = pygame.Surface((self._sub_w * 3, self._sub_h * 3))

        def at(w: int, h: int) -> tuple[int, int]:
            """Helper to convert subtile positions to pixel positions."""
            return (self._sub_w * w, self._sub_h * h)

        # Neighbor dependent non-cardinals
        if left_tile is not None:
            if not main_tile.is_top_closed and left_tile.is_top_closed:
                surface.blit(self.assets.get_static("CORNER-TOP-LEFT"),
                             at(0, 0))
            if not main_tile.is_bottom_closed and left_tile.is_bottom_closed:
                surface.blit(self.assets.get_static("CORNER-BOTTOM-LEFT"),
                             at(0, 2))
        if right_tile is not None:
            if not main_tile.is_top_closed and right_tile.is_top_closed:
                surface.blit(self.assets.get_static("CORNER-TOP-RIGHT"),
                             at(2, 0))
            if not main_tile.is_bottom_closed and right_tile.is_bottom_closed:
                surface.blit(self.assets.get_static("CORNER-BOTTOM-RIGHT"),
                             at(2, 2))
        if top_tile is not None:
            if not main_tile.is_left_closed and top_tile.is_left_closed:
                surface.blit(self.assets.get_static("CORNER-TOP-LEFT"),
                             at(0, 0))
            if not main_tile.is_right_closed and top_tile.is_right_closed:
                surface.blit(self.assets.get_static("CORNER-TOP-RIGHT"),
                             at(2, 0))
        if bottom_tile is not None:
            if not main_tile.is_left_closed and bottom_tile.is_left_closed:
                surface.blit(self.assets.get_static("CORNER-BOTTOM-LEFT"),
                             at(0, 2))
            if not main_tile.is_right_closed and bottom_tile.is_right_closed:
                surface.blit(self.assets.get_static("CORNER-BOTTOM-RIGHT"),
                             at(2, 2))

        # Block whole 3 tiles, change later
        if main_tile.is_top_closed:
            surface.blit(self.assets.get_static("WALL-TOP"), at(0, 0))
            surface.blit(self.assets.get_static("WALL-TOP"), at(1, 0))
            surface.blit(self.assets.get_static("WALL-TOP"), at(2, 0))
        if main_tile.is_right_closed:
            surface.blit(self.assets.get_static("WALL-RIGHT"), at(2, 0))
            surface.blit(self.assets.get_static("WALL-RIGHT"), at(2, 1))
            surface.blit(self.assets.get_static("WALL-RIGHT"), at(2, 2))
        if main_tile.is_bottom_closed:
            surface.blit(self.assets.get_static("WALL-BOTTOM"), at(0, 2))
            surface.blit(self.assets.get_static("WALL-BOTTOM"), at(1, 2))
            surface.blit(self.assets.get_static("WALL-BOTTOM"), at(2, 2))
        if main_tile.is_left_closed:
            surface.blit(self.assets.get_static("WALL-LEFT"), at(0, 0))
            surface.blit(self.assets.get_static("WALL-LEFT"), at(0, 1))
            surface.blit(self.assets.get_static("WALL-LEFT"), at(0, 2))

        # Corners when cardinal adjacent
        if main_tile.is_top_closed and main_tile.is_left_closed:
            surface.blit(self.assets.get_static("WALL-TOP-LEFT"), at(0, 0))
        if main_tile.is_top_closed and main_tile.is_right_closed:
            surface.blit(self.assets.get_static("WALL-TOP-RIGHT"), at(2, 0))
        if main_tile.is_bottom_closed and main_tile.is_left_closed:
            surface.blit(self.assets.get_static("WALL-BOTTOM-LEFT"), at(0, 2))
        if main_tile.is_bottom_closed and main_tile.is_right_closed:
            surface.blit(self.assets.get_static("WALL-BOTTOM-RIGHT"), at(2, 2))

        return surface

    def assemble_2x2_tile(self,
                          tl: str, tr: str,
                          bl: str, br: str) -> pygame.Surface:

        tile_surface = pygame.Surface((self._sub_w * 2, self._sub_h * 2))

        tile_surface.blit(self.assets.get_static(tl), (0, 0))
        tile_surface.blit(self.assets.get_static(tr), (self._sub_w, 0))
        tile_surface.blit(self.assets.get_static(bl), (0, self._sub_h))
        tile_surface.blit(self.assets.get_static(br), (self._sub_w,
                                                       self._sub_h))

        return tile_surface.convert_alpha()

    def assemble_3x3_tile(self,
                          tl: str, tm: str, tr: str,
                          ml: str,          mr: str,
                          bl: str, bm: str, br: str) -> pygame.Surface:

        tile_surface = pygame.Surface((self._sub_w * 3, self._sub_h * 3))

        tile_surface.blit(self.assets.get_static(tl),
                          (0, 0))
        tile_surface.blit(self.assets.get_static(tm),
                          (self._sub_w, 0))
        tile_surface.blit(self.assets.get_static(tr),
                          (self._sub_w * 2, 0))

        tile_surface.blit(self.assets.get_static(ml),
                          (0, self._sub_h))
        # tile_surface.blit(self.assets.get_static(mm),
        #                   (self._sub_w, self._sub_h))
        tile_surface.blit(self.assets.get_static(mr),
                          (self._sub_w * 2, self._sub_h))

        tile_surface.blit(self.assets.get_static(bl),
                          (0, self._sub_h * 2))
        tile_surface.blit(self.assets.get_static(bm),
                          (self._sub_w, self._sub_h * 2))
        tile_surface.blit(self.assets.get_static(br),
                          (self._sub_w * 2, self._sub_h * 2))

        return tile_surface.convert_alpha()


class StaticBackgroundElement(pygame.sprite.Sprite):

    def __init__(self, surface: pygame.Surface, x: int, y: int) -> None:
        super().__init__()

        self.image = surface
        self.rect = self.image.get_rect(topleft=(
            x * self.image.get_width(),
            y * self.image.get_height()
        ))


class Tile(BaseModel):

    is_top_closed: bool
    is_right_closed: bool
    is_bottom_closed: bool
    is_left_closed: bool

    tile_layout: Optional[pygame.Surface] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_hex_state(cls, hex: int) -> "Tile":

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

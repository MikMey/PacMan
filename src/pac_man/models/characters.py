from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass, replace
from typing import Type, Callable

import logging
import pygame
import numpy as np

from ..utils import Tile_Pos, Pixel_Pos, UnitVector
from ..render import SpriteSheetCache

from .tile import Tile

DIRECTION = {
    (0, -1): 'TOP',
    (0, 1): 'BOTTOM',
    (-1, 0): 'LEFT',
    (1, 0): 'RIGHT'
}

class CharacterName(Enum):
    PACMAN = 'PACMAN-'
    BLINKY = 'GHOST1-'
    PINKY = 'GHOST2-'
    INKY = 'GHOST3-'
    CLYDE = 'GHOST4-'

class Character(ABC, pygame.sprite.Sprite):
    """Character Parent Class"""

    def __init__(
            self,
            asset_cache: SpriteSheetCache,
            start_pos: Tile_Pos,
            subtile_size: int,
            character_name: CharacterName
            ):
        super().__init__()

        self.log = logging.getLogger('PacMan')

        self.name = character_name.value

        self.asset_cache = asset_cache
        self.subtile_size: int = subtile_size
        self.tile_size: int = subtile_size * 3

        self.is_dying = False

        # Movement attributes
        self.current_dir: UnitVector = UnitVector(0, 0)
        
        self.current_tile: Tile_Pos = replace(start_pos)
        self.target_tile: Tile_Pos = replace(start_pos)

        # Frame logic attributes
        self.current_frame = 0
        self.max_frame = -1
        self.animation_speed = 0.1
        self.animation_timer = 0.0

        self.init_image()

        # Location logic
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (
            start_pos.x * self.tile_size + self.subtile_size // 2,
            start_pos.y * self.tile_size + self.subtile_size // 2
        )

        self.speed: int = int(round(2 * self.asset_cache.scale_factor))


    def init_image(self):
        frames = self.asset_cache.get_anim(
            self.name + 'RIGHT'
        )
        self.max_frame = len(frames)
        self.image = frames[self.current_frame]


    def _dir_to_string(self, dir: UnitVector) -> str:
        """Converts :obj:`Direction` to string. Defaults to RIGHT.

        Parameters
        ----------
        dir : Direction
            Direction class to be converted.

        Returns
        -------
        str
            String indicating direction (TOP, RIGHT, LEFT, BOTTOM).

        """
        key = dir.get()
        if key not in DIRECTION.keys():
            return 'RIGHT'
        return DIRECTION[key]

    def _is_wall(self, direction: tuple, tile: Tile) -> bool:
        """Checks if next tile would be blocked.

        Parameters
        ----------
        direction : Direction
            Direction currently attempted to go to.
        tile_matrix : list[list[Tile]]
            Full matrix of Tiles to look up wall states in.

        Returns
        -------
        bool
            True if wall or border is in the way, False otherwise.

        """
        if not any(direction):
            return False

        # next_tile = replace(self.current_tile)
        # next_tile.x += self.current_dir.hori
        # next_tile.y += self.current_dir.vert

        # if not (0 <= next_tile.y < len(tile_matrix) and
        #         0 <= next_tile.x < len(tile_matrix[0])):
        #     return True

        if direction[1] == -1 and tile.is_top_closed:
            return True
        if direction[0] == 1 and tile.is_right_closed:
            return True
        if direction[1] == 1 and tile.is_bottom_closed:
            return True
        if direction[0] == -1 and tile.is_left_closed:
            return True

        return False

    def _update_frame(self, dt: float) -> None:
        """Update player frame.

        Parameters
        ----------
        dt : float
            Delta Time between loop pass.

        """
        self.animation_timer += dt

        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0.0
            self.current_frame = (self.current_frame + 1) % self.max_frame
            self.set_image()

    def _move_straight(self) -> bool:
        # change target from matrix to global map coords
        target_tile: Pixel_Pos = self.target_tile.to_pixel_pos(self.tile_size)

        # set pixel offset from topleft border
        target_tile.x += self.subtile_size // 2
        target_tile.y += self.subtile_size // 2

        # Continue if currently moving
        # print(self.rect.x, self.rect.y)
        if self.rect.x != target_tile.x or self.rect.y != target_tile.y:
            if self.rect.x < target_tile.x:
                self.rect.x += self.speed
            elif self.rect.x > target_tile.x:
                self.rect.x -= self.speed

            if self.rect.y < target_tile.y:
                self.rect.y += self.speed
            elif self.rect.y > target_tile.y:
                self.rect.y -= self.speed
            return True
        return False

    @abstractmethod
    def _update_position(self, tile_matrix) -> None:
        """Update player position if possible.

        Parameters
        ----------
        tile_matrix : list[list[Tile]]
            Full matrix of Tiles to look up wall states in.

        """
        pass

    def update(self, dt: float, tile_matrix: list[list[Tile]]) -> None:
        """Update player frame and position every frame.

        Parameters
        ----------
        dt : float
            Delta Time between loop pass.
        tile_matrix : list[list[Tile]]
            Full matrix of Tiles to look up wall states in.

        """
        self.tile_matrix = tile_matrix
        self._update_frame(dt)
        self._update_position(tile_matrix)

    @abstractmethod
    def set_image(self) -> None:
        """Get correct sprite data based on context."""
        pass


    @abstractmethod
    def kill() -> None:
        """Starts death animation."""
        pass


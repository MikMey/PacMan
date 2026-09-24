from dataclasses import replace
import time
from enum import Enum

import pygame

from ..utils import Tile_Pos, Pixel_Pos, Direction
from ..render import SpriteSheetCache

from .tile import Tile
from .characters import Character, CharacterName

class PlayerState(Enum):
	ALIVE = 0
	DEAD = 1
	RESPAWNING = 2


class Player(Character):
    """Deals with player logic."""

    def __init__(
            self,
            asset_cache: SpriteSheetCache,
            start_pos: Tile_Pos,
            subtile_size: int
            ) -> None:
        
        super().__init__(
            asset_cache=asset_cache,
            start_pos=start_pos,
            subtile_size=subtile_size,
            character_name=CharacterName.PACMAN
            )
        self.state = PlayerState.ALIVE
        
        self.buffered_dir: Direction = Direction()

        self.speed: int = int(round(2 * self.asset_cache.scale_factor))

    def set_image(self) -> None:
        if self.is_dying:
            frames = self.asset_cache.get_anim(
                self.name + "DEATH"
            )
        elif self.current_dir.is_still():
            frames = self.asset_cache.get_anim(
                self.name + self._dir_to_string(self.buffered_dir)
            )
        else:
            frames = self.asset_cache.get_anim(
                self.name + self._dir_to_string(self.current_dir)
            )

        self.max_frame = len(frames)
        self.image = frames[self.current_frame]

    def kill(self) -> None:
        
        self.is_dying = True
        self.animation_timer = 0.0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Handle WASD and arrow key input.

        Parameters
        ----------
        keys : pygame.key.ScancodeWrapper
            Keys pressed in last loop pass.

        """
        if keys[pygame.K_UP] or keys[pygame.K_w] and self.current_dir.vert != -1:
            self.buffered_dir.set(0, -1)
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.current_dir.hori != 1:
            self.buffered_dir.set(1, 0)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s] and self.current_dir.vert != 1:
            self.buffered_dir.set(0, 1)
        elif keys[pygame.K_LEFT] or keys[pygame.K_a] and self.current_dir.hori != -1:
            self.buffered_dir.set(-1, 0)

        if keys[pygame.K_KP1]:
            self.kill()

    def _update_position(self, tile_matrix: list[list[Tile]]) -> None:
        
        if self.is_dying:
            return
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

        # Check if next target is availible if exactly in middle
        else:
            self.current_tile.x = self.target_tile.x
            self.current_tile.y = self.target_tile.y

            if not self.buffered_dir.is_still() and not self._is_wall(self.buffered_dir, tile_matrix):
                self.current_dir = replace(self.buffered_dir)

            elif self._is_wall(self.current_dir, tile_matrix):
                self.current_dir.set(0, 0)

            self.target_tile.x = self.current_tile.x + self.current_dir.hori
            self.target_tile.y = self.current_tile.y + self.current_dir.vert

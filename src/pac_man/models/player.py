from dataclasses import replace
import time
from enum import Enum

import pygame

from ..utils import Tile_Pos, Pixel_Pos, UnitVector
from ..render import SpriteSheetCache

from .tile import Tile
from .characters import Character, CharacterName, DIRECTION_REVERSE

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
            character_name=CharacterName.PACMAN,
            speed_mult=1.5,
            asset_cache=asset_cache,
            start_pos=start_pos,
            subtile_size=subtile_size
            )
        self.state = PlayerState.ALIVE
        
        self.buffered_dir: UnitVector = UnitVector()

        

    def set_image(self) -> None:
        if self.state == PlayerState.DEAD:
            frames = self.asset_cache.get_anim(
                self.name + "DEATH"
            )
        elif self.state == PlayerState.RESPAWNING:
            return
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

        if keys[pygame.K_UP] or keys[pygame.K_w] and self.current_dir.y != -1:
            self.buffered_dir.set((0, -1))
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d] and self.current_dir.x != 1:
            self.buffered_dir.set((1, 0))
        elif keys[pygame.K_DOWN] or keys[pygame.K_s] and self.current_dir.y != 1:
            self.buffered_dir.set((0, 1))
        elif keys[pygame.K_LEFT] or keys[pygame.K_a] and self.current_dir.x != -1:
            self.buffered_dir.set((-1, 0))

        if keys[pygame.K_KP1]:
            self.kill()

    def _update_position(self) -> None:

        if self.state != PlayerState.ALIVE:
            return

        keys = pygame.key.get_pressed()
        self.handle_input(keys)

        if self.current_dir.get() != (0,0) and self.buffered_dir.get() == DIRECTION_REVERSE[self.current_dir.get()]:
            self.current_dir = self.buffered_dir
            self.target_tile = self.current_tile

        # Check if next target is availible if exactly in middle
        if not self._move_straight():
            self.current_tile = self.target_tile.copy()

            if not self.buffered_dir.is_still() and not self._is_wall(self.buffered_dir.get(), Tile.get_tile(self.current_tile)):
                self.current_dir = replace(self.buffered_dir)

            elif self._is_wall(self.current_dir.get(), Tile.get_tile(self.current_tile)):
                self.current_dir.set((0, 0))

            self.target_tile = Tile_Pos.get_neighbour(self.current_tile, self.current_dir)

from .structures import Tile_Pos, Pixel_Pos, Direction
from .spritesheet import SpriteSheetCache
from .tile import Tile

from dataclasses import replace
import pygame
import time


class Player(pygame.sprite.Sprite):
    """Deals with player logic."""

    def __init__(
            self,
            asset_cache: SpriteSheetCache,
            start_pos: Tile_Pos,
            subtile_size: int
            ) -> None:
        """Initialize positioning and animation logic."""
        super().__init__()
        self.asset_cache = asset_cache
        self.subtile_size: int = subtile_size
        self.tile_size: int = subtile_size * 3

        # Game logic attributes
        self.is_dying: bool = False

        # Movement attributes
        self.current_dir: Direction = Direction()
        self.buffered_dir: Direction = Direction()

        self.current_tile: Tile_Pos = replace(start_pos)
        self.target_tile: Tile_Pos = replace(start_pos)

        self.speed: int = int(round(2 * self.asset_cache.scale_factor))

        # Frame logic attributes
        self.current_frame = 0
        self.max_frame = -1
        self.animation_speed = 0.1
        self.animation_timer = 0.0
        self.set_current_image()

        # Location logic
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.topleft = (
            start_pos.x * self.tile_size + self.subtile_size // 2,
            start_pos.y * self.tile_size + self.subtile_size // 2
        )

    def kill(self) -> None:
        """Starts death animation."""

        self.is_dying = True
        self.animation_timer = 0.0

    def _dir_to_string(self, dir: Direction) -> str:
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
        if dir.vert == 1:
            return "BOTTOM"
        elif dir.vert == -1:
            return "TOP"
        elif dir.hori == -1:
            return "LEFT"
        return "RIGHT"

    def set_current_image(self) -> None:
        """Get correct sprite data based on context."""
        if self.is_dying:
            frames = self.asset_cache.get_anim("PACMAN-DEATH")
        elif self.current_dir.is_still():
            frames = self.asset_cache.get_anim(
                "PACMAN-" + self._dir_to_string(self.buffered_dir))
        else:
            frames = self.asset_cache.get_anim(
                "PACMAN-" + self._dir_to_string(self.current_dir))

        self.max_frame = len(frames)
        self.image = frames[self.current_frame]

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

    def _is_wall(self, direction: Direction,
                 tile_matrix: list[list[Tile]]) -> bool:
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
        # if direction.is_still():
        #     return False

        next_tile = replace(self.current_tile)
        next_tile.x += self.current_dir.hori
        next_tile.y += self.current_dir.vert

        if not (0 <= next_tile.y < len(tile_matrix) and
                0 <= next_tile.x < len(tile_matrix[0])):
            return True

        tile = tile_matrix[self.current_tile.y][self.current_tile.x]
        if direction.vert == -1 and tile.is_top_closed:
            return True
        if direction.hori == 1 and tile.is_right_closed:
            return True
        if direction.vert == 1 and tile.is_bottom_closed:
            return True
        if direction.hori == -1 and tile.is_left_closed:
            return True

        return False

    def update(self, dt: float, tile_matrix: list[list[Tile]]) -> None:
        """Update player frame and position every frame.

        Parameters
        ----------
        dt : float
            Delta Time between loop pass.
        tile_matrix : list[list[Tile]]
            Full matrix of Tiles to look up wall states in.

        """
        self._update_frame(dt)
        self._update_position(tile_matrix)

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
            self.set_current_image()

    def _update_position(self, tile_matrix: list[list[Tile]]) -> None:
        """Update player position if possible.

        Parameters
        ----------
        tile_matrix : list[list[Tile]]
            Full matrix of Tiles to look up wall states in.

        """
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

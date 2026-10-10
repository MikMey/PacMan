
from random import randrange
import functools
import sys
from typing import Any
import random
import pygame
import logging
from pydantic import ValidationError

from ..utils import Tile_Pos, Config
from ..utils.configuration import LevelMetadata
from ..render import SpriteSheetCache, Hud
from ..models import TileSpriteFactory, Tile, GhostPersonality, \
    StaticSpriteElement, TILE_SIZE, SUBTILE_SIZE, \
    Player, Ghost, GhostState, PlayerState
from .states import State


class Level(State):
    """Sprite and loop logic for the main game level."""

    def __init__(self,
                 hex_matrix: list[list[int]],
                 screen: pygame.Surface,
                 level: LevelMetadata,
                 config: Config
                 ) -> None:
        """Create sprites that are needed in level."""
        self.log = logging.getLogger('PacMan')

        self.screen = screen
        self.data = level
        self.rows = self.data.height
        self.columns = self.data.width
        self.config = config

        self.tile_matrix = self.create_tile_matrix(hex_matrix)

        self.freeze = False

        self.init_level_size(
            self.columns,
            self.rows,
            self.screen.get_width(),
            self.screen.get_height()
        )

        self.populate_sprite_groups()

    def init_level_size(self,
                        columns: int,
                        rows: int,
                        screen_w: int,
                        screen_h: int
                        ) -> None:
        """Initialize level scaling and size"""

        raw_level_h = rows * TILE_SIZE
        raw_level_w = columns * TILE_SIZE

        max_level_w = float(screen_w * 0.9)
        max_level_h = float(screen_h * 0.8)

        self.scale_factor = min(
            max_level_w // raw_level_w,
            max_level_h // raw_level_h
        )

        try:
            self.asset_cache: SpriteSheetCache =\
                SpriteSheetCache.from_default_file_path(
                    scale_factor=self.scale_factor
                )
        except ValidationError as e:
            sys.exit(str(e))

        level_screen_w = int(raw_level_w * self.scale_factor)

        self.horizontal_padding = int(level_screen_w * 0.1)
        self.vertical_padding = int(screen_h * 0.1)

        surface_w = int(columns *
                        TILE_SIZE *
                        self.asset_cache.scale_factor)
        surface_h = int(rows *
                        TILE_SIZE *
                        self.asset_cache.scale_factor)

        self.display_surface = pygame.Surface((surface_w, surface_h))

        self.position = pygame.Vector2(
            (screen_w - surface_w) // 2,  # horizontal_padding,
            self.vertical_padding
        )

    def create_tile_matrix(
            self,
            hex_matrix: list[list[int]]
            ) -> list[list[Tile]]:
        """Converts MazeGenerator hex numbers to tile classes matrix."""
        matrix: list[list[Tile]] = []
        for y, row in enumerate(hex_matrix):
            matrix.append([])
            for x, item in enumerate(row):
                matrix[y].append(Tile.create(item, x, y))
        Tile.set_matrix(matrix)
        for row in matrix:  # type: ignore
            for item in row:
                item.create_reference()  # type: ignore
        return matrix

    def init_characters(self) -> None:
        """add instances of ghost class for each ghost to ghost_group"""

        start_pos = Tile_Pos(self.columns // 2, self.rows // 2)
        tile: Tile = Tile.get_tile(start_pos)
        if not tile.neighbours or tile.neighbours == []:
            start_pos.add(Tile_Pos(-1, 0))

        self.player_group: pygame.sprite.Group = pygame.sprite.Group()
        self.pacman = Player(
            asset_cache=self.asset_cache,
            start_pos=start_pos,
            subtile_size=self.subtile_size
            )
        self.player_group.add(self.pacman)

        self.ghost_group: pygame.sprite.Group = pygame.sprite.Group()

        PrepGhost = functools.partial(
            Ghost,
            asset_cache=self.asset_cache,
            subtile_size=self.subtile_size,
            player=self.pacman)

        self.inky: Ghost = PrepGhost(
            start_pos=Tile_Pos(0, 0),
            ghost_peronality=GhostPersonality.INKY
        )
        self.clyde: Ghost = PrepGhost(
            start_pos=Tile_Pos(self.columns - 1, 0),
            ghost_peronality=GhostPersonality.CLYDE
        )
        self.blinky: Ghost = PrepGhost(
            start_pos=Tile_Pos(0, self.rows - 1),
            ghost_peronality=GhostPersonality.BLINKY
        )
        self.pinky: Ghost = PrepGhost(
            start_pos=Tile_Pos(self.columns - 1, self.rows - 1),
            ghost_peronality=GhostPersonality.PINKY
        )

        self.ghost_group.add(self.pinky, self.inky, self.blinky, self.clyde)

    def reload_tile_sheet(self) -> None:
        """Reloads tile sprites to match new offset selection."""
        self.tile_group.empty()
        tile_factory = TileSpriteFactory(assets=self.asset_cache)

        for y in range(len(self.tile_matrix)):
            for x in range(len(self.tile_matrix[y])):
                tile = self.tile_matrix[y][x]

                self.tile_group.add(StaticSpriteElement.from_relative(
                    tile_factory.from_tile(
                        tile=tile
                    ),
                    x=x,
                    y=y
                ))

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""

        self.tile_group: pygame.sprite.Group =\
            pygame.sprite.Group()  # Tiles without pacgums
        self.gum_group: pygame.sprite.Group =\
            pygame.sprite.Group()  # Pacgums
        self.super_gum_group: pygame.sprite.Group =\
            pygame.sprite.Group()  # Super Pacgums
        self.fruit_group: pygame.sprite.Group =\
            pygame.sprite.Group()  # Decorative Fruits

        tile_factory = TileSpriteFactory(assets=self.asset_cache)

        possible_pacgums: list[tuple[int, int]] = []

        for y in range(len(self.tile_matrix)):
            for x in range(len(self.tile_matrix[y])):
                main_tile: Tile = self.tile_matrix[y][x]

                self.tile_group.add(StaticSpriteElement.from_relative(
                    tile_factory.from_tile(
                        tile=main_tile
                    ),
                    x=x,
                    y=y
                ))
                if main_tile.neighbours == []:
                    rand_fruit = self.asset_cache.get_static(
                                 f"FRUIT-{randrange(8)}")
                    self.fruit_group.add(StaticSpriteElement.from_pixel(
                        rand_fruit,
                        x=(x * self.asset_cache.scale_factor * TILE_SIZE +
                           (self.asset_cache.scale_factor
                            * SUBTILE_SIZE) // 2),
                        y=(y * self.asset_cache.scale_factor * TILE_SIZE +
                           (self.asset_cache.scale_factor
                            * SUBTILE_SIZE) // 2),
                    ))
                else:
                    possible_pacgums.append((x * 3 + 1, y * 3 + 1))

                if not main_tile.is_top_closed:
                    possible_pacgums.append((x * 3 + 1, y * 3))
                if not main_tile.is_right_closed:
                    possible_pacgums.append((x * 3 + 2, y * 3 + 1))
                if not main_tile.is_bottom_closed:
                    possible_pacgums.append((x * 3 + 1, y * 3 + 2))
                if not main_tile.is_left_closed:
                    possible_pacgums.append((x * 3, y * 3 + 1))

        gum = self.data.pacgums
        s_gums = self.data.super_pacgums
        if gum == 0:
            gum = len(possible_pacgums)

        while possible_pacgums and gum > 0:
            idx = random.randrange(len(possible_pacgums))
            pos = possible_pacgums.pop(idx)

            if s_gums > 0:
                self.super_gum_group.add(StaticSpriteElement.from_relative(
                    tile_factory.get_item("super_pacgum"),
                    x=pos[0],
                    y=pos[1]
                ))
                s_gums -= 1
            else:
                self.gum_group.add(StaticSpriteElement.from_relative(
                    tile_factory.get_item("pacgum"),
                    x=pos[0],
                    y=pos[1]
                ))
            gum -= 1

        self.subtile_size = tile_factory._sub_w
        self.init_characters()

    def check_collission(self, obj: pygame.sprite.Group) -> Any:
        """Checks collision of pacman with a given sprite group."""
        possible_collisions = pygame.sprite.spritecollide(
            self.pacman,  # type: ignore
            obj,
            False
        )

        eat_radius = 5 * self.asset_cache.scale_factor

        objs = []

        for item in possible_collisions:
            dx = self.pacman.rect.centerx - item.rect.centerx
            dy = self.pacman.rect.centery - item.rect.centery
            distance_squared = (dx ** 2) + (dy ** 2)

            if distance_squared < (eat_radius ** 2):
                objs.append(item)
        return objs

    def switch_ghosts(self) -> None:
        """Changes the ghosts state to scared."""
        for ghost in self.ghost_group:
            if ghost.state != GhostState.RESPAWNING:
                ghost.count = 0
                ghost.state = GhostState.FLEEING

    def collission_logic(self) -> bool:
        """Eats pacgums and ghosts depending on logic."""

        # ghost
        items: list = self.check_collission(self.ghost_group)
        for item in items:
            if item.state == GhostState.ROAMING:
                self.pacman.state = PlayerState.DEAD
                self.start_tick = 0
            elif item.state == GhostState.FLEEING:
                Hud.score += self.config.points_per_ghost
                item.state = GhostState.RESPAWNING

        # pacgum
        items = self.check_collission(self.gum_group)
        for item in items:
            Hud.score += self.config.points_per_pacgum
            item.kill()
            if len(self.gum_group) == 0 and len(self.super_gum_group) == 0:
                return True

        # superpacgum
        items = self.check_collission(self.super_gum_group)
        for item in items:
            Hud.score += self.config.points_per_super_pacgum
            self.switch_ghosts()
            item.kill()
            if len(self.gum_group) == 0 and len(self.super_gum_group) == 0:
                return True

        return False

    def render(self) -> None:
        """Draws all groups."""
        self.tile_group.draw(self.display_surface)
        self.gum_group.draw(self.display_surface)
        self.super_gum_group.draw(self.display_surface)
        self.fruit_group.draw(self.display_surface)
        self.ghost_group.draw(self.display_surface)
        self.player_group.draw(self.display_surface)
        self.screen.blit(self.display_surface, self.position)

    def run(self, dt: float) -> bool:
        """Update and display loop to be run every frame.

        Parameters
        ----------
        dt : float
            Delta time used for updating sprites.

        """

        if not self.freeze:
            self.ghost_group.update(dt, self.tile_matrix)
        self.player_group.update(dt, self.tile_matrix)
        rc = self.collission_logic()
        self.render()

        return rc

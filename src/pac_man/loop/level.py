
from random import randrange
import functools
import sys
from typing import Any

import pygame
import logging
from pydantic import ValidationError

from ..utils import Tile_Pos
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
                 columns: int,
                 rows: int
                 ) -> None:
        """Create sprites that are needed in level."""
        self.log = logging.getLogger('PacMan')

        self.screen = screen
        self.rows = rows
        self.columns = columns

        self.tile_matrix = self.create_tile_matrix(hex_matrix)

        self.freeze = False

        self.init_level_size(
            columns,
            rows,
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
            sys.exit(str(e), style="red", markup=False, highlight=False)

        level_screen_w = int(raw_level_w * self.scale_factor)
        # level_screen_h = int(raw_level_h * self.scale_factor)

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
        for row in matrix:
            for item in row:
                item.create_reference()
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
        self.tile_group.empty()

        tile_factory = TileSpriteFactory(assets=self.asset_cache)

        # maze_x = len(self.tile_matrix[0])
        # maze_y = len(self.tile_matrix)

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
            pygame.sprite.Group()  # Pacgums and such
        self.fruit_group: pygame.sprite.Group =\
            pygame.sprite.Group()  # Decorative Fruits

        tile_factory = TileSpriteFactory(assets=self.asset_cache)

        # maze_x = len(self.tile_matrix[0])
        # maze_y = len(self.tile_matrix)

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
                    # self.log.debug(f"neigh={main_tile.neighbours}")
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
                    self.gum_group.add(StaticSpriteElement.from_relative(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 1,
                        y=y * 3 + 1
                    ))

                if not main_tile.is_top_closed:
                    self.gum_group.add(StaticSpriteElement.from_relative(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 1,
                        y=y * 3
                    ))
                if not main_tile.is_right_closed:
                    self.gum_group.add(StaticSpriteElement.from_relative(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 2,
                        y=y * 3 + 1
                    ))
                if not main_tile.is_bottom_closed:
                    self.gum_group.add(StaticSpriteElement.from_relative(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 1,
                        y=y * 3 + 2
                    ))
                if not main_tile.is_left_closed:
                    self.gum_group.add(StaticSpriteElement.from_relative(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3,
                        y=y * 3 + 1
                    ))

        self.subtile_size = tile_factory._sub_w
        self.init_characters()

    def check_collission(self, obj: pygame.sprite.Group) -> Any:
        possible_collisions = pygame.sprite.spritecollide(
            self.pacman,  # type: ignore
            obj,
            False
        )

        eat_radius = 5 * self.asset_cache.scale_factor

        for item in possible_collisions:
            dx = self.pacman.rect.centerx - item.rect.centerx
            dy = self.pacman.rect.centery - item.rect.centery
            distance_squared = (dx ** 2) + (dy ** 2)

            if distance_squared < (eat_radius ** 2):
                return item

    def collission_logic(self) -> None:
        # superpacgum

        # ghost
        item: Ghost = self.check_collission(self.ghost_group)
        if item:
            if item.state == GhostState.ROAMING:
                self.pacman.state = PlayerState.DEAD
                self.start_tick = 0
            elif item.state == GhostState.FLEEING:
                item.state = GhostState.RESPAWNING

        # pacgum
        item = self.check_collission(self.gum_group)
        if item:
            Hud.score += 1
            item.kill()

    def render(self) -> None:
        # self.display_surface.fill((140, 40, 40))
        self.tile_group.draw(self.display_surface)
        self.gum_group.draw(self.display_surface)
        self.fruit_group.draw(self.display_surface)
        self.ghost_group.draw(self.display_surface)
        self.player_group.draw(self.display_surface)

        self.screen.blit(self.display_surface, self.position)

    def run(self, dt: float) -> bool:
        """
        Update and display loop to be run every frame.

        Parameters
        ----------
        dt : float
            Delta time used for updating sprites.

        """

        # self.handle_player_state(dt)
        if not self.freeze:
            self.ghost_group.update(dt, self.tile_matrix)
        self.player_group.update(dt, self.tile_matrix)
        self.collission_logic()
        self.render()

        return self.pacman.state == PlayerState.ALIVE

from .structures import Tile_Pos
from .spritesheet import SpriteSheetCache
from .tile import TileSpriteFactory, Tile, StaticBackgroundElement
from .player import Player
from .text import TextSpriteFactory

import pygame


class Level:
    """Sprite and loop logic for the main game level."""

    def __init__(self, hex_matrix: list[list[int]],
                 asset_cache: SpriteSheetCache,
                 screen: pygame.Surface) -> None:
        """Create sprites that are needed in level."""
        self.asset_cache = asset_cache
        self.tile_matrix = self.hex_to_tile_matrix(hex_matrix)
        self.screen = screen

        # Tiles without pacgums
        self.bg_group = pygame.sprite.Group()
        # Text and numbers
        self.text_group = pygame.sprite.Group()
        # Pacgums and such
        self.item_group = pygame.sprite.Group()
        # Pacman
        self.player_group = pygame.sprite.Group()

        self.populate_sprite_groups()

    def hex_to_tile_matrix(self,
                           hex_matrix: list[list[int]]) -> list[list[Tile]]:
        """Converts MazeGenerator hex numbers to tile classes matrix."""
        return [[Tile.from_hex_state(hex) for hex in row]
                for row in hex_matrix]

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""
        tile_factory = TileSpriteFactory(assets=self.asset_cache)
        text_factory = TextSpriteFactory(assets=self.asset_cache)

        maze_x = len(self.tile_matrix[0])
        maze_y = len(self.tile_matrix)

        for y in range(len(self.tile_matrix)):
            for x in range(len(self.tile_matrix[y])):
                main_tile = self.tile_matrix[y][x]

                self.bg_group.add(StaticBackgroundElement(
                    tile_factory.from_tile(
                        main_tile=main_tile,
                        top_tile=self.tile_matrix[y-1][x] if y > 0 else None,
                        right_tile=(self.tile_matrix[y][x+1]
                                    if x < maze_x-1 else None),
                        bottom_tile=(self.tile_matrix[y+1][x]
                                     if y < maze_y-1 else None),
                        left_tile=self.tile_matrix[y][x-1] if x > 0 else None,
                    ),
                    x=x,
                    y=y
                ))
                self.item_group.add(StaticBackgroundElement(
                    tile_factory.get_item(tile=main_tile),
                    x=x * 3 + 1,
                    y=y * 3 + 1
                ))

                if not main_tile.is_top_closed:
                    self.item_group.add(StaticBackgroundElement(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 1,
                        y=y * 3
                    ))
                if not main_tile.is_right_closed:
                    self.item_group.add(StaticBackgroundElement(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 2,
                        y=y * 3 + 1
                    ))
                if not main_tile.is_bottom_closed:
                    self.item_group.add(StaticBackgroundElement(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3 + 1,
                        y=y * 3 + 2
                    ))
                if not main_tile.is_left_closed:
                    self.item_group.add(StaticBackgroundElement(
                        tile_factory.get_item(tile=main_tile),
                        x=x * 3,
                        y=y * 3 + 1
                    ))

        self.text_group.add(StaticBackgroundElement(
            text_factory.from_string(s="HIGH SCORE"),
            x=2,
            y=0
        ))

        self.pacman = Player(
            asset_cache=self.asset_cache,
            start_pos=Tile_Pos(0, 0),
            subtile_size=tile_factory._sub_w,
            subtile_mult=3
        )
        self.player_group.add(self.pacman)

    def loop(self, dt: float) -> None:
        """Update and display loop to be run every frame.

        Parameters
        ----------
        dt : float
            Delta time used for updating sprites.

        """
        keys = pygame.key.get_pressed()
        self.pacman.handle_input(keys)

        self.player_group.update(dt, self.tile_matrix)

        # items_eaten = pygame.sprite.spritecollide(
        #     self.pacman, self.item_group, True)  # type: ignore

        # if items_eaten:
        #     pass

        possible_collisions = pygame.sprite.spritecollide(
            self.pacman,  # type: ignore
            self.item_group,
            False
        )

        items_eaten = []
        eat_radius = 10

        for item in possible_collisions:
            dx = self.pacman.rect.centerx - item.rect.centerx
            dy = self.pacman.rect.centery - item.rect.centery
            distance_squared = (dx * dx) + (dy * dy)

            if distance_squared < (eat_radius * eat_radius):
                items_eaten.append(item)

        for item in items_eaten:
            item.kill()

        self.screen.fill((140, 40, 40))
        self.bg_group.draw(self.screen)
        self.item_group.draw(self.screen)
        self.player_group.draw(self.screen)
        self.text_group.draw(self.screen)

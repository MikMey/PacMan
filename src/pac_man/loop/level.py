
import pygame
from random import randrange

from ..utils import Tile_Pos
from ..render import SpriteSheetCache, Hud
from ..models import TileSpriteFactory, Tile, StaticSpriteElement,TILE_SIZE, SUBTILE_SIZE, Player


class Level:
    """Sprite and loop logic for the main game level."""

    def __init__(self, hex_matrix: list[list[int]],
                 asset_cache: SpriteSheetCache,
                 screen: pygame.Surface,
                 hud: Hud,
                 horizontal_padding: int,
                 vertical_padding: int) -> None:
        """Create sprites that are needed in level."""
        self.asset_cache = asset_cache
        self.tile_matrix = self.hex_to_tile_matrix(hex_matrix)
        self.screen = screen
        self.hud = hud

        total_rows = len(self.tile_matrix)
        total_cols = len(self.tile_matrix[0])

        surface_w = int(total_cols * TILE_SIZE * self.asset_cache.scale_factor)
        surface_h = int(total_rows * TILE_SIZE * self.asset_cache.scale_factor)

        self.display_surface = pygame.Surface((surface_w, surface_h))

        self.position = pygame.Vector2(
            (self.screen.get_width() - surface_w) // 2,  # horizontal_padding,
            vertical_padding
        )

        self.tile_group = pygame.sprite.Group()  # Tiles without pacgums
        self.gum_group = pygame.sprite.Group()  # Pacgums and such
        self.fruit_group = pygame.sprite.Group()  # Decorative Fruits
        self.player_group = pygame.sprite.Group()  # Pacman

        self.populate_sprite_groups()

    def hex_to_tile_matrix(self,
                           hex_matrix: list[list[int]]) -> list[list[Tile]]:
        """Converts MazeGenerator hex numbers to tile classes matrix."""
        return [[Tile.from_hex_state(hex) for hex in row]
                for row in hex_matrix]

    def populate_sprite_groups(self) -> None:
        """Add sprites needed in level to sprite groups."""
        tile_factory = TileSpriteFactory(assets=self.asset_cache)

        maze_x = len(self.tile_matrix[0])
        maze_y = len(self.tile_matrix)

        for y in range(len(self.tile_matrix)):
            for x in range(len(self.tile_matrix[y])):
                main_tile = self.tile_matrix[y][x]

                self.tile_group.add(StaticSpriteElement.from_relative(
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
                if (main_tile.is_top_closed and
                        main_tile.is_right_closed and
                        main_tile.is_bottom_closed and
                        main_tile.is_left_closed):
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

        self.pacman = Player(
            asset_cache=self.asset_cache,
            start_pos=Tile_Pos(0, 0),
            subtile_size=tile_factory._sub_w
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

        possible_collisions = pygame.sprite.spritecollide(
            self.pacman,  # type: ignore
            self.gum_group,
            False
        )

        items_eaten = []
        eat_radius = 5 * self.asset_cache.scale_factor

        for item in possible_collisions:
            dx = self.pacman.rect.centerx - item.rect.centerx
            dy = self.pacman.rect.centery - item.rect.centery
            distance_squared = (dx ** 2) + (dy ** 2)

            if distance_squared < (eat_radius ** 2):
                items_eaten.append(item)

        for item in items_eaten:
            self.hud.add_score(1)
            item.kill()

        # self.display_surface.fill((140, 40, 40))
        self.tile_group.draw(self.display_surface)
        self.gum_group.draw(self.display_surface)
        self.fruit_group.draw(self.display_surface)
        self.player_group.draw(self.display_surface)

        self.screen.blit(self.display_surface, self.position)
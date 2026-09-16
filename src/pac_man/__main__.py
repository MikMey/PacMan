from .configuration import Config
from .spritesheet import SpriteSheetCache
from .tile import TileSpriteFactory, StaticBackgroundElement, Tile

from mazegenerator import MazeGenerator
from pydantic import ValidationError
from rich.console import Console
import pygame


# class StaticBackgroundElement(pygame.sprite.Sprite):

#     def __init__(self, assets: SpriteSheetCache,
#                  asset_name: str, x: int, y: int) -> None:
#         super().__init__()
#         self.image = assets.get_static(asset_name)
#         self.rect = self.image.get_rect(topleft=(
#             x * self.image.get_width(),
#             y * self.image.get_height()
#         ))


def main() -> int:

    console = Console()

    try:
        config = Config.from_argv_file()
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    console.print(str(config))

    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Pac-Man")
    clock = pygame.time.Clock()

    SCALE_FACTOR = 6
    try:
        assets = SpriteSheetCache.from_default_file_path(SCALE_FACTOR)
    except ValidationError as e:
        console.print(str(e), style="red", markup=False, highlight=False)
        return 1

    factory = TileSpriteFactory(assets=assets)
    # test_tile = factory.assemble_3x3_tile(
    #     tl="WALL-TOP-LEFT", tm="WALL-TOP", tr="WALL-TOP-RIGHT",
    #     ml="WALL-LEFT",                     mr="WALL-RIGHT",
    #     bl="WALL-BOTTOM-LEFT", bm="WALL-BOTTOM", br="WALL-BOTTOM-RIGHT",
    # )

    bg_group = pygame.sprite.Group()
    # bg_group.add(StaticBackgroundElement(test_tile, x=0, y=1))

    maze_x, maze_y = 5, 5
    maze_matrix = MazeGenerator(size=(maze_x, maze_y), seed=3).maze
    tile_matrix = [[Tile.from_hex_state(hex) for hex in row]
                   for row in maze_matrix]

    for y in range(len(tile_matrix)):
        for x in range(len(tile_matrix[y])):
            bg_group.add(StaticBackgroundElement(
                factory.from_tile(
                    main_tile=tile_matrix[y][x],
                    top_tile=tile_matrix[y-1][x] if y > 0 else None,
                    right_tile=tile_matrix[y][x+1] if x < maze_x-1 else None,
                    bottom_tile=tile_matrix[y+1][x] if y < maze_y-1 else None,
                    left_tile=tile_matrix[y][x-1] if x > 0 else None,
                ),
                x=x,
                y=y
            ))

    print(maze_matrix)
    print(tile_matrix)

    running = True
    while running:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill((140, 40, 40))
        bg_group.draw(screen)

        pygame.display.flip()

    pygame.quit()

    return 0


if __name__ == "__main__":
    main()

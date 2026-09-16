from .configuration import Config
from .spritesheet import SpriteSheetCache

from pydantic import ValidationError
from rich.console import Console
import pygame


class StaticBackgroundElement(pygame.sprite.Sprite):

    def __init__(self, assets: SpriteSheetCache,
                 asset_name: str, x: int, y: int) -> None:
        super().__init__()
        self.image = assets.get_static(asset_name)
        self.rect = self.image.get_rect(topleft=(
            x * self.image.get_width(),
            y * self.image.get_height()
        ))


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

    bg_group = pygame.sprite.Group()
    for i in range(5):
        bg_block = StaticBackgroundElement(
            assets,
            "B-B",
            x=i,
            y=1
        )
        bg_group.add(bg_block)

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

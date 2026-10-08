import sys
import time

import pygame
from pydantic import ValidationError

from ..render import SpriteSheetCache

from .states import State, LoopState

START_MENU: list[list[str | None]] = [
            [None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None,
             None, None],

            [None, None, None, None, None, None, None, "CHAR-P",
             "CHAR-A", "CHAR-C", "CHAR--", "CHAR-M", "CHAR-A",
             "CHAR-N", None, None, None, None],
            [None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None],
            [None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None],

            [None, None, None, None, "CORNER-TOP-LEFT", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "CORNER-TOP-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None, None,
             None, None, None, None, None, None, None, None,
             "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None, None,
             "CHAR-S", "CHAR-T", "CHAR-A", "CHAR-R", "CHAR-T", None,
             None, None, "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None, None,
             None, None, None, None, None, None, None, None,
             "BORDER-RIGHT", None],
            [None, None, None, None, "CORNER-BOTTOM-LEFT", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "CORNER-BOTTOM-RIGHT", None],

            [None, None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None],

            [None, None, None, None, "CORNER-TOP-LEFT", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "CORNER-TOP-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None, None,
             None, None, None, None, None, None, None, None,
             "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, "CHAR-H", "CHAR-I",
             "CHAR-G", "CHAR-H", "CHAR-S", "CHAR-C", "CHAR-O", "CHAR-R",
             "CHAR-E", None, "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None, None, None,
             None, None, None, None, None, None, None, "BORDER-RIGHT", None],
            [None, None, None, None, "CORNER-BOTTOM-LEFT", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "CORNER-BOTTOM-RIGHT", None],

            [None, None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None],

            [None, None, None, None, "CORNER-TOP-LEFT", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "BORDER-TOP", "BORDER-TOP",
             "BORDER-TOP", "BORDER-TOP", "CORNER-TOP-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None,
             None, None, None, None, None, None, None, None,
             None, "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None,
             None, "CHAR-Q", "CHAR-U", "CHAR-I", "CHAR-T", None,
             None, None, None, "BORDER-RIGHT", None],
            [None, None, None, None, "BORDER-LEFT", None, None,
             None, None, None, None, None, None, None, None,
             None, "BORDER-RIGHT", None],
            [None, None, None, None, "CORNER-BOTTOM-LEFT",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "BORDER-BOTTOM",
             "BORDER-BOTTOM", "BORDER-BOTTOM", "CORNER-BOTTOM-RIGHT",
             None],

            [None, None, None, None, None, None, None, None,
             None, None, None, None, None, None, None, None, None, None]
        ]

# WIDTH
MAX_LETTERS = 9
BOX_BUFFER = 1
PACMAN_BUFFER = 2
WIDTH_MULT = MAX_LETTERS + BOX_BUFFER*2 + PACMAN_BUFFER

# HEIGHT
MAX_BOXES = 5
BOX_HEIGHT = 5
BUFFER = 1
HEIGHT_MULT = MAX_BOXES*(BOX_HEIGHT + BUFFER) + BUFFER

SUBTILE_SIZE = 8
TILE_SIZE = SUBTILE_SIZE * 3

START = 0
HIGHSCORE = 1
QUIT = 2


class Selector(pygame.sprite.Sprite):
    def __init__(self, scale_factor: int) -> None:
        super().__init__()
        self.selector_cache =\
            SpriteSheetCache.from_default_file_path(scale_factor * 1.5)
        self.image: pygame.Surface =\
            self.selector_cache.get_static("S-PACMAN-RIGHT")
        self.rect: pygame.Rect = self.image.get_rect()
        self.rect.y += int(SUBTILE_SIZE *
                           self.selector_cache.scale_factor *
                           3 + SUBTILE_SIZE)


class MainMenu(State):
    state: list[LoopState] = [
        LoopState.GAME_LOOP,
        LoopState.SHOW_HIGHSCORE,
        LoopState.END_GAME
    ]

    def __init__(self, screen: pygame.Surface) -> None:

        self.screen = screen
        self.curr = START

        self.scale_factor = min(
            self.screen.get_width() // (WIDTH_MULT * SUBTILE_SIZE),
            self.screen.get_height() // (HEIGHT_MULT * SUBTILE_SIZE)
        )

        try:
            self.asset_cache: SpriteSheetCache =\
                SpriteSheetCache.from_default_file_path(
                    scale_factor=self.scale_factor
                )
        except ValidationError as e:
            sys.exit(f"{e}")

        surface_w = int(len(START_MENU[0]) *
                        SUBTILE_SIZE *
                        self.asset_cache.scale_factor)
        surface_h = int(len(START_MENU) *
                        SUBTILE_SIZE *
                        self.asset_cache.scale_factor)
        self.surface = pygame.Surface((surface_w, surface_h))

        self.position = pygame.Vector2(
            (self.screen.get_width() - surface_w) // 2,  # horizontal_padding,
            SUBTILE_SIZE * 3
        )

        self.init_draw()

    def init_draw(self) -> None:

        self.menu_group: pygame.sprite.Group = pygame.sprite.Group()

        for y, row in enumerate(START_MENU):
            self._group_add_name(
                self.asset_cache,
                self.menu_group,
                row,
                [0, y]
                )

        self.selector_group: pygame.sprite.Group = pygame.sprite.Group()
        self.selector = Selector(self.scale_factor)
        self.selector_group.add(self.selector)

    def handle_input(self) -> None:  # type: ignore
        if self.keys[pygame.K_w]:
            if self.curr == 0:
                self.selector.rect.y += int(
                    SUBTILE_SIZE *
                    self.selector.selector_cache.scale_factor *
                    4)*2
            else:
                self.selector.rect.y -= int(
                    SUBTILE_SIZE *
                    self.selector.selector_cache.scale_factor *
                    4)
            self.curr = (self.curr - 1) % 3
        elif self.keys[pygame.K_s]:
            if self.curr == 2:
                self.selector.rect.y -= int(
                    SUBTILE_SIZE *
                    self.selector.selector_cache.scale_factor *
                    4)*2
            else:
                self.selector.rect.y += int(
                    SUBTILE_SIZE *
                    self.selector.selector_cache.scale_factor
                    * 4
                    )
            self.curr = (self.curr + 1) % 3

    def render(self) -> None:
        self.surface.fill(0)
        self.menu_group.draw(self.surface)
        self.selector_group.draw(self.surface)
        self.screen.blit(self.surface, self.position)

    def run(self) -> LoopState:
        self.keys = pygame.key.get_pressed()
        if self.keys[pygame.K_SPACE]:
            return MainMenu.state[self.curr]
        self.handle_input()

        self.render()
        time.sleep(0.15)
        return LoopState.MAIN_MENU

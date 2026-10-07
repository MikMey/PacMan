import time
import json
import sys
from typing import Optional

import pygame

from ..models import StaticSpriteElement
from ..render import SpriteSheetCache

from .states import State, LoopState

SUBTILE_SIZE = 8
TILE_SIZE = SUBTILE_SIZE * 3

class _BaseHighscore():

    screen: pygame.Surface = None
    highscore_file: str = None

    def __init__(self, highscore_file: Optional[str], screen: Optional[pygame.Surface]):
        if not _BaseHighscore.screen:
            _BaseHighscore.screen = screen
        self.screen = _BaseHighscore.screen
        if not _BaseHighscore.highscore_file:
            _BaseHighscore.highscore_file = highscore_file
        self.highscore_file = _BaseHighscore.highscore_file
        scale_factor = min(
            self.screen.get_width() // (SUBTILE_SIZE * 22),
            self.screen.get_height() // (SUBTILE_SIZE * 22)
        )
        self.asset_cache = SpriteSheetCache.from_default_file_path(scale_factor)

        surface_w = int(22 * SUBTILE_SIZE * self.asset_cache.scale_factor)
        surface_h = int(22 * SUBTILE_SIZE * self.asset_cache.scale_factor)
        self.surface = pygame.Surface((surface_w, surface_h))

        self.position = pygame.Vector2(
            (self.screen.get_width() - surface_w) // 2,  # horizontal_padding,
            SUBTILE_SIZE * 3
        )
        

    def _get_highscore(self):
        try:
            with open(self.highscore_file, 'r') as f:
                raw_highscores: str = f.read()
                if not raw_highscores or not len(raw_highscores) or raw_highscores == 'null':
                    highscores = {}
                else:
                    highscores = json.loads(raw_highscores)
        except json.decoder.JSONDecodeError as err:
            sys.exit(f"Invalid json file:\n{err}")
        except (PermissionError, OSError, FileNotFoundError,
                IsADirectoryError) as err:
            sys.exit(f"Provided file path is incorrect:\n{err}")
        except Exception as err:
            sys.exit(f"Error:\n{err}")
        return highscores


class ShowHighscore(_BaseHighscore, State):

    highscore: int = 0

    def __init__(self, highscore_file: Optional[str], screen: Optional[pygame.Surface]):
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)
        highscores = self._get_highscore()
        self._prep_sprite(highscores)

    def _prep_sprite(self, highscores: dict[str, int]):
        self._scores_group: pygame.sprite.Group = pygame.sprite.Group()
        for key, value in highscores.items():
            if not(isinstance(key, str) and key.isalnum() and isinstance(value, int) and value >= 0):
                return
        highscores = {key: value for key, value in sorted(highscores.items(), key=lambda item: item[1], reverse=True)}
        self._group_add_str(self.asset_cache, self._scores_group, "highscore", [0, 0])
        y = 2
        for key, value in highscores.items():
            if value > ShowHighscore.highscore:
                ShowHighscore.highscore = value
            self._group_add_str(self.asset_cache, self._scores_group, key, [0, y])
            self._group_add_str(self.asset_cache, self._scores_group, str(value), [11, y])
            y+=2

    def run(self, state):
        self.state = state
        self._scores_group.draw(self.surface)
        self.screen.blit(self.surface, self.position)

class EnterHighscore(_BaseHighscore, State):

    def __init__(self, highscore_file: Optional[str], screen: Optional[pygame.Surface]):
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)

    def _validate_score(self, highscores: dict[str, int], score: int):
        if highscores and highscores != {}:
            to_check = min(highscores.values())
            if score <= to_check and len(highscores.items()) >= 10:
                return
            if len(highscores.items()) >= 10 and self.player_name not in highscores.keys():
                for key, value in highscores.copy().items():
                    if value == to_check:
                        highscores.pop(key)
        if len(self.player_name) and self.player_name not in highscores.keys() or highscores[self.player_name] > score:
            highscores[self.player_name] = score
        return highscores


    def _write_highscore(self, content: dict):
        try:
            with open(self.highscore_file, 'w') as f:
                json.dump(content, f)
        except json.decoder.JSONDecodeError as err:
            sys.exit(f"Invalid json file:\n{err}")
        except (PermissionError, OSError, FileNotFoundError,
                IsADirectoryError) as err:
            sys.exit(f"Provided file path is incorrect:\n{err}")
        except Exception as err:
            sys.exit(f"Error:\n{err}")


    def _get_name(self):
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    self.confirmed = False
                if event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                if event.key <= 255 and len(self.player_name) < 10:
                    char = chr(event.key)
                    if char.isalnum():
                        self.player_name += char.upper()
            for i in range(len(self.slots)):
                if len(self.player_name) >= i + 1 and self.player_name[i]:
                    self.slots[i].image = self.asset_cache.get_static("CHAR-" + self.player_name[i].upper())
                else:
                    self.slots[i].image = self.asset_cache.get_static("CHAR--")

    def _prep_sprites_enter(self):
        self._enter_group: pygame.sprite.Group = pygame.sprite.Group()

        self.slots: list[StaticSpriteElement] = []
        self._group_add_str(self.asset_cache, self._enter_group, "enter name", [0, 0])
        for x in range(10):
            self.slots.append(
                StaticSpriteElement.from_pixel(
                    self.asset_cache.get_static("CHAR--"),
                    (x+1) * self.asset_cache.scale_factor * SUBTILE_SIZE,
                    2 * self.asset_cache.scale_factor * SUBTILE_SIZE
                )
            )
            self._enter_group.add(self.slots[x])


    def run(self, score):
        if not score:
            score = 0
        self.player_name = ""
        self.confirmed = True
        self._prep_sprites_enter()
        while self.confirmed == True:
            time.sleep(0.01)
            self._enter_group.draw(self.surface)
            self.screen.blit(self.surface, self.position)
            pygame.display.flip()
            self._get_name()
        if not self.player_name or self.player_name == '':
            return
        highscores = self._get_highscore()
        highscores = self._validate_score(highscores, score)
        self._write_highscore(highscores)
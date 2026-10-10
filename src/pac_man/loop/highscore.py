import time
import json
import sys
from typing import Optional
import functools
import pygame

from ..models import StaticSpriteElement
from ..render import SpriteSheetCache
from .states import State, LoopState

SUBTILE_SIZE = 8
TILE_SIZE = SUBTILE_SIZE * 3


class _BaseHighscore():
    """Parent class for classes dealing with highscores.

    Attributes
    ----------
    screen : pygame.Surface
        Main pydantic window screen.
    highscore_file : str
        Highscore file name from config.

    Raises
    ------
    ValueError
        When highscore content is invalid.

    """
    screen: pygame.Surface = None  # type: ignore
    highscore_file: str = None  # type: ignore

    def __init__(
            self,
            highscore_file: Optional[str],
            screen: Optional[pygame.Surface]
    ):
        """Initializes scale factor and asset cache."""
        if not _BaseHighscore.screen:
            _BaseHighscore.screen = screen  # type: ignore
        self.screen: pygame.Surface = _BaseHighscore.screen
        if not _BaseHighscore.highscore_file:
            _BaseHighscore.highscore_file = highscore_file  # type: ignore
        self.highscore_file: str = _BaseHighscore.highscore_file
        scale_factor = min(
            self.screen.get_width() // (SUBTILE_SIZE * 22),
            self.screen.get_height() // (SUBTILE_SIZE * 22)
        )
        self.asset_cache =\
            SpriteSheetCache.from_default_file_path(scale_factor)

        surface_w = int(22 * SUBTILE_SIZE * self.asset_cache.scale_factor)
        surface_h = int(22 * SUBTILE_SIZE * self.asset_cache.scale_factor)
        self.surface = pygame.Surface((surface_w, surface_h))

        self.position = pygame.Vector2(
            (self.screen.get_width() - surface_w) // 2,
            SUBTILE_SIZE * 3
        )

    def _get_highscore(self) -> dict[str, int]:
        """Returns a dictionary of highscore content.

        Returns
        -------
        dict[str, int]
            Dictionary of NAME: SCORE.

        Raises
        ------
        ValueError
            When highscore content is invalid or a list.

        """
        try:
            with open(self.highscore_file, 'r') as f:
                raw_highscores: str = f.read()

                if (
                    not raw_highscores or not
                    len(raw_highscores) or
                    raw_highscores == 'null'
                ):
                    highscores = {}
                else:
                    highscores = json.loads(raw_highscores)

                if isinstance(highscores, list):
                    raise ValueError("Highscore cannot be a list")
        except json.decoder.JSONDecodeError as err:
            sys.exit(f"Invalid json file:\n{err}")
        except (PermissionError, OSError, FileNotFoundError,
                IsADirectoryError) as err:
            sys.exit(f"Provided file path is incorrect:\n{err}")
        except Exception as err:
            sys.exit(f"Error:\n{err}")
        return highscores


class ShowHighscore(_BaseHighscore, State):
    """State that shows the leaderboard.

    Attributes
    ----------
    highscore : int
        Highscore achieved by the player.

    """
    highscore: int = 0

    def __init__(self,
                 highscore_file: Optional[str],
                 screen: Optional[pygame.Surface]):
        """Gets and prepares the sprites for the leaderboard."""
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)
        highscores = self._get_highscore()
        self._prep_sprite(highscores)

    def _prep_sprite(self, highscores: dict[str, int]) -> None:
        """Fills _scores_group with correct sprites.

        Parameters
        ----------
        highscores : dict[str, int]
            Dictionary of NAME: SCORE.

        """
        self._scores_group: pygame.sprite.Group = pygame.sprite.Group()
        for key, value in highscores.items():
            if (
                not
                (isinstance(key, str) and
                    key.isalnum() and
                    isinstance(value, int) and
                    value >= 0)
            ):
                return
        highscores = {
            key: value
            for key, value in sorted(highscores.items(),
                                     key=lambda item: item[1], reverse=True)}
        self._group_add_str(
            self.asset_cache,
            self._scores_group,
            "highscore",
            [0, 0])
        y = 2
        for key, value in highscores.items():
            if value > ShowHighscore.highscore:
                ShowHighscore.highscore = value
            self._group_add_str(self.asset_cache,
                                self._scores_group,
                                key,
                                [0, y])
            self._group_add_str(self.asset_cache,
                                self._scores_group,
                                str(value),
                                [11, y])
            y += 2

    def handle_input(self, key_event: pygame.event.Event) -> None:
        """Returns to main menu when called."""
        self.state = LoopState.MAIN_MENU

    def run(self) -> LoopState:
        """Draws prepared sprites.

        Returns
        -------
        LoopState
            SHOW_HIGHSCORE to stay, MAIN_MENU on key press.

        """
        self.state = LoopState.SHOW_HIGHSCORE
        self._scores_group.draw(self.surface)
        self.screen.blit(self.surface, self.position)
        self.handle_event()
        return self.state


class EnterHighscore(_BaseHighscore, State):
    """State that waits for typing the name for the leaderboard."""

    def __init__(self,
                 highscore_file: Optional[str],
                 screen: Optional[pygame.Surface]):
        """Calls parent inits."""
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)

    def _validate_score(self,
                        highscores: dict[str, int],
                        score: int
                        ) -> dict[str, int]:
        """Updates highscore capped at 10 entries.

        Parameters
        ----------
        highscores : dict[str, int]
            Current Content of dictionary of NAME: SCORE.
        score : int
            New score that may be added if applicable.

        Returns
        -------
        dict[str, int]
            New dictionary of NAME: SCORE with score maybe added.

        """
        if self.player_name in highscores:
            if score > highscores[self.player_name]:
                highscores[self.player_name] = score
            return highscores

        if len(highscores) >= 10:
            lowest_score = min(highscores.values())
            if score <= lowest_score:
                return highscores

            for k, v in list(highscores.items()):
                if v == lowest_score:
                    highscores.pop(k)
                    break

        if len(self.player_name):
            highscores[self.player_name] = score

        return highscores

    def _write_highscore(self, content: dict) -> None:
        """Writes new content to highscore file.

        Parameters
        ----------
        content : dict
            Content of dictionary of NAME: SCORE.

        """
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

    def _get_name(self) -> None:
        """Listens to alphanum character and misc to write name."""
        for event in pygame.event.get():
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_RETURN or
                        event.key == pygame.K_ESCAPE):
                    self.confirmed = False
                if event.key == pygame.K_BACKSPACE:
                    self.player_name: str = self.player_name[:-1]
                if event.key <= 255 and len(self.player_name) < 10:
                    char = chr(event.key)
                    if char.isalnum():
                        self.player_name += char.upper()
            for i in range(len(self.slots)):
                if len(self.player_name) >= i + 1 and self.player_name[i]:
                    self.slots[i].image =\
                        self.asset_cache.get_static(
                            "CHAR-" + self.player_name[i].upper()
                            )
                else:
                    self.slots[i].image = self.asset_cache.get_static("CHAR--")

    def _prep_sprites_enter(self, score: int) -> None:
        """Populates _enter_group with static text.

        Parameters
        ----------
        score : int
            Score achieved by player.

        """
        self._enter_group: pygame.sprite.Group = pygame.sprite.Group()

        self.slots: list[StaticSpriteElement] = []
        self._group_add_str(
            self.asset_cache,
            self._enter_group,
            'game over',
            [0, 0])
        self._group_add_str(
            self.asset_cache,
            self._enter_group,
            f'score {score}',
            [0, 2])
        self._group_add_str(
            self.asset_cache,
            self._enter_group,
            "enter name",
            [0, 4])
        for x in range(10):
            self.slots.append(
                StaticSpriteElement.from_pixel(
                    self.asset_cache.get_static("CHAR--"),
                    (x+1) * self.asset_cache.scale_factor * SUBTILE_SIZE,
                    6 * self.asset_cache.scale_factor * SUBTILE_SIZE
                )
            )
            self._enter_group.add(self.slots[x])

    def run(self, score: int) -> None:
        """Runs entering name together to score and updates highscore file.

        Parameters
        ----------
        score : int
            Score achived.

        """
        if not score:
            score = 0
        self.player_name = ""
        self.confirmed = True
        self._prep_sprites_enter(score)
        while self.confirmed is True:
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


class Guide(_BaseHighscore, State):
    """Deals with the control information display found in main menu."""

    def __init__(self,
                 highscore_file: Optional[str],
                 screen: Optional[pygame.Surface]):
        """Initializes and prepares sprites."""
        if _BaseHighscore.highscore_file and _BaseHighscore.screen:
            super().__init__(None, None)
        else:
            super().__init__(highscore_file, screen)
        self._prep_sprites_enter()

    def _prep_sprites_enter(self) -> None:
        """Prepares sprites."""
        self._guide: pygame.sprite.Group = pygame.sprite.Group()

        prep = functools.partial(
            self._group_add_str,
            self.asset_cache,
            self._guide
        )

        def entry(row: int, action: str, key: str) -> None:
            prep("..........", [0, row])
            prep(action, [0, row])
            prep(key, [9, row])

        prep("GAMEPLAY", [4.5, 0])
        entry(1, "move", "wasd/arrow")
        entry(2, "pause", "space")
        entry(3, "quit", "esc")

        prep("CHEAT", [4.5, 5])
        entry(6, "skip", "enter")
        entry(7, "death", "kp1")
        entry(8, "1up", "kp2")
        entry(9, "freeze", "kp3")
        entry(10, "scare", "kp5")
        entry(11, "fast", "pageup")
        entry(12, "slow", "pagedown")

        prep("VISUAL", [4.5, 14])
        entry(15, "text", "kp7")
        entry(16, "walls", "kp8")

    def handle_input(self, key_event: pygame.event.Event) -> None:
        """Returns to main menu when called."""
        self.state = LoopState.MAIN_MENU

    def run(self) -> LoopState:
        """Draws sprites and waits for any input to return to menu."""
        self.state = LoopState.GUIDE
        self._guide.draw(self.surface)
        self.screen.blit(self.surface, self.position)
        self.handle_event()
        return self.state

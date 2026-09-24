from enum import Enum
from typing import Callable
import random
import time
from dataclasses import dataclass
from typing import Optional

from ..utils import Tile_Pos, Pixel_Pos, UnitVector
from ..render import SpriteSheetCache

from .characters import CharacterName, Character
from .player import Player
from .tile import Tile

@dataclass
class Bfs_Obj:
    pos: Tile_Pos
    cost: int
    origin: Optional["Bfs_Obj"] = None

    def get_neighbour(self) -> "list[Bfs_Obj]":
        res: "list[Bfs_Obj]" = []
        tile: Tile = Tile.get_tile(self.pos)
        if not tile.is_bottom_closed:
            obj = Bfs_Obj(
                Tile_Pos(self.pos.x, self.pos.y + 1),
                self.cost + 1,
                origin=self
                )
            res.append(obj)
        if not tile.is_top_closed:
            obj = Bfs_Obj(
                Tile_Pos(self.pos.x, self.pos.y - 1),
                self.cost + 1,
                origin=self
                )
            res.append(obj)
        if not tile.is_right_closed:
            obj = Bfs_Obj(
                Tile_Pos(self.pos.x + 1, self.pos.y),
                self.cost + 1,
                origin=self
                )
            res.append(obj)
        if not tile.is_left_closed:
            obj = Bfs_Obj(
                Tile_Pos(self.pos.x - 1, self.pos.y),
                self.cost + 1,
                origin=self
                )
            res.append(obj)
        return res


class GhostState(Enum):
    ROAMING = 0
    FLEEING = 1
    RESPAWNING = 2

class GhostPersonality(Enum):

    BLINKY: Callable = 'blinky'
    PINKY: Callable = 'pinky'
    INKY: Callable = 'inky'
    CLYDE: Callable = 'clyde'

class Ghost(Character):

    def __init__(
            self,
            asset_cache: SpriteSheetCache,
            start_pos: Tile_Pos,
            ghost_peronality: GhostPersonality,
            player: Player,
            subtile_size: int
            ) -> None:

        super().__init__(
            asset_cache=asset_cache,
            start_pos=start_pos,
            subtile_size=subtile_size,
            character_name=CharacterName[ghost_peronality.name]
            )

        self.ghost_name = ghost_peronality
        self.player: Player = player
        self.state: GhostState = GhostState.ROAMING
        self.speed: int = int(round(1.6 * self.asset_cache.scale_factor))

    def set_image(self):
        if self.state == GhostState.RESPAWNING:
            frames = self.asset_cache.get_anim(
                'GHOST-DEAD' + self._dir_to_string(self.current_dir)
            )
        elif self.state == GhostState.FLEEING:
            frames = self.asset_cache.get_anim(
                self.name + "SCARED"
            )
        else:
            frames = self.asset_cache.get_anim(
                self.name + self._dir_to_string(self.current_dir)
            )
        self.max_frame = len(frames)
        self.image = frames[self.current_frame]

    def kill():
        pass

    def _update_position(self, tile_matrix) -> None:
        self.current_dir.set((0, 1))
        if not self._move_straight():
            self.current_tile = self.target_tile.copy()

            if self._is_wall(self.current_dir.get(), Tile.get_tile(self.current_tile)):
                self.log.debug('func call')
                func: Callable = self.__getattribute__(self.ghost_name.value)
                func()

            self.target_tile = Tile_Pos.get_neighbour(self.current_tile, self.current_dir)


    def blinky(self):
        """Direct chase; flee top right"""
        if self.state == GhostState.ROAMING:
            self.log.debug('blinky call')
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(self.player.current_tile.x + 1, self.player.current_tile.y)
                )
        elif self.state == GhostState.FLEEING:
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(len(self.tile_matrix[0]) - 1, 0)
                )
        else:
            pass


    def pinky(self):
        """Chase 2 tiles to right of pacman; flee top left"""
        if self.state == GhostState.ROAMING:
            self.log.debug('pinky call')
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(self.player.current_tile.x + 1, self.player.current_tile.y)
                )
        elif self.state == GhostState.FLEEING:
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(0, 0)
                )
        else:
            pass

    def inky(self):
        """go left (1/5 go right); flee bottom right"""
        self.log.debug('inky call')

        TURN_LEFT = {
            (1,0): (0,1),
            (0,1): (-1,0),
            (-1,0): (0,-1),
            (0,-1): (1,0)
        }
        if self.state == GhostState.ROAMING:
            turn = self.current_dir.get()
            while True:
                turn = TURN_LEFT[turn]
                if not self._is_wall(turn, self.tile_matrix):
                    self.current_dir.set()
                    break
                self.log.debug(f"turn={turn}")
        elif self.state == GhostState.FLEEING:
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(len(self.tile_matrix[0]) - 1, len(self.tile_matrix) - 1)
                )
        else:
            pass
        self.log.debug('inky finish')

    def clyde(self):
        """move random at intersection; flee bottom left"""
        self.log.debug('clyde call')
        CHANGE = [
            (1,0),
            (0,1),
            (-1,0),
            (0,-1)
        ]
        if self.state == GhostState.ROAMING:
            while True:
                res = random.randint(0,3)
                direction = CHANGE[res]
                if not self._is_wall(direction, self.tile_matrix):
                    self.current_dir.set(direction)
                    break
        elif self.state == GhostState.FLEEING:
            self.current_dir = self.bfs(
                Tile_Pos(self.current_tile.x, self.current_tile.y),
                Tile_Pos(0, len(self.tile_matrix) - 1)
                )
        else:
            pass


    def bfs(self, pos: Tile_Pos, target: Tile_Pos):
        self.log.debug('bfs call')
        new_target: Bfs_Obj = Bfs_Obj(target, 0)
        tiles: list[Bfs_Obj] = [new_target]
        queue: list = [new_target]
        while queue:
            time.sleep(0.1)
            self.log.debug(f'pos={pos} target={target}\n\n\tqueue={queue}\n\n\ttiles={tiles}')
            curr: Bfs_Obj = queue.pop(0)
            neighbours: list[Bfs_Obj] = curr.get_neighbour()
            for item in neighbours:
                queue.append(item)
                tiles.append(item)
            for obj in tiles:
                if obj.pos == pos:
                    queue = None
                    break
        for obj in tiles:
            if obj.pos == pos:
                return obj.origin.pos
        return None

        

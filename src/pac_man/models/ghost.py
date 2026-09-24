from enum import Enum
from typing import Callable
import random

from ..utils import Tile_Pos, Pixel_Pos, Direction
from ..render import SpriteSheetCache

from .characters import CharacterName, Character
from .player import Player
from .tile import Tile

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
				self.name + 'RESPAWN' #TODO match to correct strings
            )
		elif self.state == GhostState.FLEEING:
			frames = self.asset_cache.get_anim(
				self.name + "FLEE-" + self._dir_to_string(self.current_dir)
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
		self.current_dir.set(0, 1)
		if not self._move_straight():
			self.current_tile.x = self.target_tile.x
			self.current_tile.y = self.target_tile.y
			if self._is_wall((self.current_dir.hori, self.current_dir.vert), self.tile_matrix):
				self.log.debug('func call')
				func: Callable = self.__getattribute__(self.ghost_name.value)
				func()

			self.target_tile.x = self.current_tile.x + self.current_dir.hori
			self.target_tile.y = self.current_tile.y + self.current_dir.vert


	def blinky(self):
		"""Direct chase; flee top right"""
		if self.state == GhostState.ROAMING:
			self.log.debug('blinky call')
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[self.player.current_tile.x + 1, self.player.current_tile.y]
				)
		elif self.state == GhostState.FLEEING:
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[len(self.tile_matrix[0]) - 1, 0]
				)
		else:
			pass


	def pinky(self):
		"""Chase 2 tiles to right of pacman; flee top left"""
		if self.state == GhostState.ROAMING:
			self.log.debug('pinky call')
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[self.player.current_tile.x + 1, self.player.current_tile.y]
				)
		elif self.state == GhostState.FLEEING:
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[0, 0]
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
			turn = (self.current_dir.hori, self.current_dir.vert)
			while True:
				turn = TURN_LEFT[turn]
				if not self._is_wall(turn, self.tile_matrix):
					self.current_dir.vert = turn[0]
					self.current_dir.hori = turn[1]
					break
				self.log.debug(f"turn={turn}")
		elif self.state == GhostState.FLEEING:
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[len(self.tile_matrix[0]) - 1, len(self.tile_matrix) - 1]
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
				direct = CHANGE[res]
				if not self._is_wall(direct, self.tile_matrix):
					self.current_dir.vert = direct[1]
					self.current_dir.hori = direct[0]
					break
		elif self.state == GhostState.FLEEING:
			self.current_dir = self.dfs(
				[self.current_tile.x, self.current_tile.y],
				[0, len(self.tile_matrix) - 1]
				)
		else:
			pass

	
	def dfs(self, pos: list, target: list):
		self.log.debug('dfs call')
		move: list = [0, 0]
		final: Direction = Direction()
		moves = []
		curr_pos = pos
		while curr_pos != target:
			change = [
				target[0] - curr_pos[0],
				target[1] - curr_pos[1]
			]
			self.log.debug(f"curr={curr_pos}, target={target}, move={move}, change={change}")
			tile: Tile = self.tile_matrix[pos[1]][pos[0]]
			if abs(change[0]) > abs(change[1]):
				if change[0] > 0 and not tile.is_right_closed:
					move = [1, 0]
				elif not tile.is_left_closed:
					move = [-1, 0]
				else:
					if change[1] > 0 and not tile.is_bottom_closed:
						move = [0, 1]
					else:
						move = [0, -1]
			moves.append(move)
			curr_pos = [
				curr_pos[0] + move[0],
				curr_pos[1] + move[1]
			]
		if pos in moves:
			i = moves.index(pos)
			final.set(
				moves[i + 1][0],
				moves[i + 1][1]
			)
		else:
			final.set(
				moves[0][0],
				moves[0][1]
			)
		return final


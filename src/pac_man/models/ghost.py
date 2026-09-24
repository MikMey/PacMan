from enum import Enum
from typing import Callable

from ..utils import Tile_Pos, Pixel_Pos, Direction
from ..render import SpriteSheetCache

from .characters import CharacterName, Character

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
            subtile_size: int
            ) -> None:
		
		super().__init__(
            asset_cache=asset_cache,
            start_pos=start_pos,
            subtile_size=subtile_size,
            character_name=CharacterName[ghost_peronality.name]
            )

		self.state: GhostState = GhostState.ROAMING

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
		pass

	def blinky():
		"""Direct chase; flee top right"""
		pass

	def pinky():
		"""Chase 2 tiles in front of pacman; flee top left"""
		pass

	def inky():
		"""go left (1/5 go right); flee bottom right"""
		pass

	def clyde():
		"""move random at intersection; flee bottom left"""
		pass


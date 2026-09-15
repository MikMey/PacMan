import numpy as np

from .models import Tile, Player, Ghost

class Map:

	def __init__(self):
		pass

	def create_map(self, maze: list[list[int]]) -> list[list[Tile]]:
		"""
		map of tiles as np.array[Tile]
		"""
		x = 0
		y = 0
		tiles:list[list[Tile]] = []
		for line in maze:
			tiles.append([])
			for walls in line:
				tile = Tile([x,y], walls)
				tiles[y].append(tile)
				x += 1
			y += 1
		return np.array(tiles, object)
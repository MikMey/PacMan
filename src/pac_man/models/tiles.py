
WALLS = {
	'N': 1,
	'E': 2,
	'S': 4,
	'W': 8
}

class Tile:

	def __init__(self, position: list, walls: int):
		self.position: list = position
		self.pacgum: bool = False
		self.super_pacgum: bool = False
		
		self._set_walls(walls)

	def _set_walls(self, walls: int) -> None:
		"""
		set walls based on bitwise walls var
		"""
		self.north: bool = False
		self.east: bool = False
		self.south: bool = False
		self.west: bool = False
		if (WALLS['N'] & walls):
			self.north = True
		if (WALLS['E'] & walls):
			self.east = True
		if (WALLS['S'] & walls):
			self.south = True
		if (WALLS['W'] & walls):
			self.west = True

	def set_pacgum(self) -> bool:
		"""
		Returns True on success
		"""
		if self.pacgum or self.super_pacgum:
			return False
		self.pacgum = True
		return True

	def set_super_pacgum(self) -> bool:
		"""
		Returns True on success
		"""
		if self.pacgum or self.super_pacgum:
			return False
		self.super_pacgum = True
		return True

		1100
from abc import ABC, abstractmethod
from enum import Enum
from dataclasses import dataclass
from typing import Type, Callable

import numpy as np

class GhostPersonality(Enum):

	def blinky():
		pass

	def pinky():
		pass

	def inky():
		pass

	def clyde():
		pass

	BLINKY: Callable = blinky
	PINKY: Callable = pinky
	INKY: Callable = inky
	CLYDE: Callable = clyde


class GhostState(Enum):
	ROAMING = 0
	FLEEING = 1
	RESPAWNING = 2

class PlayerState(Enum):
	ALIVE = 0
	DEAD = 1
	RESPAWNING = 2

class Character(ABC):

	def __init__(self, position: list):
		self.position = np.array(position, np.float32)
		self.velocity = np.array([], np.float32)

class Player(Character):

	def __init__(self, position: list):
		super().__init__(position)

class Ghost(Character):

	def __init__(self, position: list, name: GhostPersonality):
		super().__init__(position)
		self.name = name
		self.state: GhostState = GhostState.RESPAWNING


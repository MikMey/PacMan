from abc import ABC, abstractmethod

class State(ABC):
	def __int__(self, state):
		self.state = state

	@abstractmethod
	def run(self):
		pass
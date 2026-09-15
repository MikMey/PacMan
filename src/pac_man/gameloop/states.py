from abc import ABC, abstractmethod

class State(ABC):
	def __int__(self):
		pass

	@abstractmethod
	def run(self):
		pass
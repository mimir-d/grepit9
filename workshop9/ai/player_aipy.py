## ECHIPA:


##	800x800
##
from ants import PlayerAI
import math

class Player(PlayerAI):

	def __init__(self):
		super(Player, self).__init__('AIPY')
		self.counter = 0

		self.targets = [[400, 440],
						[420, 420],
						[440, 400],
						[420, 380],
						[400, 360],
						[380, 380],
						[360, 400],
						[380, 420]]
		self.curr = 0

	def update(self, player_positions, player_lives, food_positions):
		if math.fabs(self.position[0] - self.targets[self.curr][0]) < 2 and math.fabs(self.position[1] - self.targets[self.curr][1]) < 2:
			self.curr += 1

		if self.curr == 8: self.curr = 0
		return	self.targets[self.curr][0] - self.position[0], self.targets[self.curr][1] - self.position[1]


	# 	self.counter += 1
	# 	if self.counter == 100:
	# 		self.counter = 0
	# 		self.lastPositions = player_positions

	# def dist(x0, y0, x1, y1):
	# 	return (((x0-x1) * (x0-x1) + (y0-y1)*(y0-y1)) ** 0.5)

	# def computeDistances(self, pos, food):
	# 	for f in food:
	# 		for p in player
	# 			if(p[0] == self.position[0] and self)
	# 			d = dist(self.position[0], self.position[1], f[0], f[1])

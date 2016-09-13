

from ants import PlayerAI


def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5

def determinant(x, y, z):
	return 1.0*x[0]*(y[1] - z[1]) - x[1]*(y[0] - z[0]) + y[0]*z[1] - y[1] * z[0]


class Player(PlayerAI):


	def __init__(self):
		super(Player, self).__init__('Brasov')
		self.last_player_positions = None

	def update(self, player_positions, player_lives, food_positions):
			if(self.last_player_positions == None):
				self.last_player_positions = player_positions
			closest_food = (400, 400)
			min_dist = 10000000
			for f in food_positions:
				d = dist(self.position[0], self.position[1], f[0], f[1])
				ok = True
				i = 0
				while(i < len(player_positions)):
					enemy = player_positions[i]
					det = determinant(self.last_player_positions[i], player_positions[i], f);
					if d - 0.0001 >  dist(enemy[0], enemy[1], f[0], f[1]) and  det == 0:
						ok = False
					i = i + 1

				if d < min_dist and ok:
					min_dist = d
					closest_food = f

			self.last_player_positions = player_positions;
			return closest_food[0] - self.position[0], closest_food[1] - self.position[1]

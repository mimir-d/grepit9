

from ants import PlayerAI


def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5


class Player(PlayerAI):
    def __init__(self):
        super(Player, self).__init__('Demo4')

    def update(self, player_positions, food_positions):
        closest_food = None

        min_dist = 10000000
        for f in food_positions:
            d = dist(self.position[0], self.position[1], f[0], f[1])
            if d < min_dist:
                min_dist = d
                closest_food = f

        return closest_food[0] - self.position[0], closest_food[1] - self.position[1]

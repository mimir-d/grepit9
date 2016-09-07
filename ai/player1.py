

from ants import PlayerAI


def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5


class Player(PlayerAI):
    def __init__(self):
        super(Player, self).__init__('Player1')

    def update(self, player_positions, food_positions):
        closest_food = None

        min_dist = 1000
        print(food_positions)
        for f in food_positions:
            d = dist(self.position[0], self.position[1], f[0], f[1])
            print(d)
            if d < min_dist:
                d = min_dist
                closest_food = f

        print('>>', self.position)
        return closest_food[0] - self.position[0], closest_food[1] - self.position[1]

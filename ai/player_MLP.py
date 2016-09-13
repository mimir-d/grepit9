

from ants import PlayerAI


def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5
delayrrr=0


class Player(PlayerAI):
    delayrrr=0
    def __init__(self):
        super(Player, self).__init__('MLP')
        delayrrr=0

    def update(self, player_positions, player_lives, food_positions):
        global delayrrr
        closest_food = None

        min_dist = 10000000
        for f in food_positions:
            d = dist(self.position[0], self.position[1], f[0], f[1])
            if d < min_dist:
                min_dist = d
                closest_food = f
        delayrrr=delayrrr+1
        if delayrrr<1000:
            return 420-self.position[0], 420-self.position[1]
        if delayrrr<5000:
            closest_food=food_positions[0]
            for f in food_positions:
                min_dist = 1000000
                closest_player = self
                for d in player_positions:
                    distance=dist(d[0],d[1],f[0],f[1])
                    if distance < min_dist:
                        min_dist = distance
                        closest_player = d
                if closest_player == self:
                    if dist(closest_food[0],closest_food[1],self[0],self[1])>dist(f[0],f[1],self[0],self[1]):
                        closest_food = f
        return closest_food[0] - self.position[0], closest_food[1] - self.position[1]

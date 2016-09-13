from array import array

from ants import PlayerAI
from math import *
import datetime

def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5

def intersects(p1, s1, p2, s2):
    if (areaOfIntersection(p1[0], p1[1], s1, p2[0], p2[1], s2) > 0.0):
        return True
    return False

def areaOfIntersection(x0, y0, r0, x1, y1, r1):
        rr0 = r0 * r0;
        rr1 = r1 * r1;
        d = sqrt((x1 - x0) * (x1 - x0) + (y1 - y0) * (y1 - y0));

  # Circles do not overlap
        if (d > r1 + r0):
            return 0
  # Circle1 is completely inside circle0
        elif (d <= abs(r0 - r1) and r0 >= r1):
    # Return area of circle1
            return pi * rr1

  # Circle0 is completely inside circle1
        elif (d <= abs(r0 - r1) and r0 < r1):
    # Return area of circle0
            return pi * rr0

  # Circles partially overlap
        else:
            phi = (acos((rr0 + (d * d) - rr1) / (2 * r0 * d))) * 2
            theta = (acos((rr1 + (d * d) - rr0) / (2 * r1 * d))) * 2
            area1 = 0.5 * theta * rr1 - 0.5 * rr1 * sin(theta)
            area2 = 0.5 * phi * rr0 - 0.5 * rr0 * sin(phi)
    # Return area of intersection
        return area1 + area2

class Player(PlayerAI):

    FR = 12
    BIGFR = 80
    PR = 25
    WIDTH = 800
    HEIGHT = 800
    SAFEZONE = 28
    global prevTime

    global playersHp
    playersHp = []
    def __init__(self):
        global playersHp
        super(Player, self).__init__('Alfa-fanina v2')
        for i in range(0, 1000):
            playersHp.append(1)
        self.prevTime = datetime.datetime.now()

    def update(self, player_positions, player_lives, food_positions):
        pos = -1
        min = 10000
        for i, k in enumerate(player_positions):
            if (k[0] != self.position[0] and k[1] != self.position[1] and intersects(self.position, self.SAFEZONE, k, self.PR)):
                if (dist(self.position[0], self.position[1], k[0], k[1]) < min):
                    min = dist(self.position[0], self.position[1], k[0], k[1])
                    pos = i
        if (pos != -1): #and player_health[pos] - self.life > -10):
            return self.position[0] - player_positions[pos][0], self.position[1]-player_positions[pos][1]
        crtTime = datetime.datetime.now()
        dt = (crtTime - self.prevTime).total_seconds()

        for i,k in enumerate(player_positions):
            for j,k2 in enumerate(player_positions):
                if playersHp[i] > 0 and playersHp[j] > 0 and fabs(playersHp[i] - playersHp[j]) > 3 and intersects(k, self.PR, k2, self.PR):
                    playersHp[i] -= dt
                    playersHp[j] -= dt
                    closest_food = None
        for i, k in enumerate(player_positions):
            for j, k2, in enumerate(food_positions):
                if playersHp[i] > 0 and intersects(k, self.PR, k2, self.FR):
                    playersHp[i] += 1;
        for i, k in enumerate(player_positions):
            if intersects(k, self.PR, [self.WIDTH/2, self.HEIGHT/2], self.BIGFR):
                playersHp[i] += 0.1 * dt;

        closest_food = None

        min_dist = 10000000
        for f in food_positions:
            if f[0] < self.WIDTH-10 and f[1] < self.HEIGHT-10 and f[0] > 10 and f[1] > 10:
                d = dist(self.position[0], self.position[1], f[0], f[1])

                #closest = check_point(d,player_positions,f) - FOR REFACTORING
                closest = True
                player = 0
                while player<len(player_positions):
                    distance = dist(player_positions[player][0], player_positions[player][1], f[0], f[1])
                    if distance < d:
                        closest = False
                    player = player + 1

                if closest and d < min_dist:
                    min_dist = d
                    closest_food = f

        #If can't find a safe closest target, go to the safe center
        if closest_food is None:
            closest_food = (300,500)
        self.prevTime = crtTime

        return closest_food[0] - self.position[0], closest_food[1] - self.position[1]






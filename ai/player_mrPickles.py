from ants import PlayerAI

def dist(x0, y0, x1, y1):
    return ((x0-x1)*(x0-x1) + (y0-y1)*(y0-y1)) ** 0.5

def keepInsideMap(distX, distY, posX, posY, diameter):
    if (distX + posX - diameter <= 0):
        distX = diameter - posX
    if (distX + posX + diameter >= 800):
        distX = 800 - posX - diameter

    if (distY + posY - diameter <= 0):
        distY = diameter - posY
    if (distY + posY + diameter >= 800):
        distY = 800 - posY - diameter
    return distX, distY

class Player(PlayerAI):
    def __init__(self):
        super(Player, self).__init__('Mr. Pickles')

    def update(self, player_positions, player_lives, food_positions):

        closest_food = None
        diameter = 25
        radius = diameter / 2

        avoiding = False

        foodMinDist = 10000000

        foodDistances = []
        playerDistances = []

        foundPreviousTarget = False

        for foodIndex, foodPos in enumerate(food_positions):
            distance = dist(self.position[0], self.position[1], foodPos[0], foodPos[1])
            foodDistances.insert(foodIndex, distance)
            if(hasattr(self, 'previousTarget') and self.previousTarget[0] == foodPos[0] and self.previousTarget[1] == foodPos[1]):
                foundPreviousTarget = True
            if (distance < foodMinDist):
                foodMinDist = distance
                closest_food = foodPos

        for playerIndex, playerPos in enumerate(player_positions):
            if not(playerPos[0] == self.position[0] and playerPos[1] == self.position[1]):
                distance = dist(self.position[0], self.position[1], playerPos[0], playerPos[1])
                playerDistances.insert(playerIndex, distance)

        dangerousPlayers = []
        minDanger = [999999, 999999]
        minDist = 99999
        for playerIndex, playerDist in enumerate(playerDistances):
            if (playerDist < diameter * 2):
                avoiding = True
                dangerousPlayers.append(player_positions[playerIndex])
                currDist = abs(dist(self.position[0], self.position[1], minDanger[0], minDanger[1]))
                if (currDist < minDist):
                    minDanger = player_positions[playerIndex]
                    minDist = currDist

        bestFoodDistX = closest_food[0] - self.position[0]
        bestFoodDistY = closest_food[1] - self.position[1]

        if (not(foundPreviousTarget)):
            self.previousTarget = closest_food

        distX = 400 - radius - self.position[0]
        distY = 400 - radius - self.position[1]

        if not(avoiding):
            distX = bestFoodDistX
            distY = bestFoodDistY
        else:
            if (minDanger[0] <= self.position[0] and minDanger[1] <= self.position[1]):
                distX = 1
                distY = 1
            elif (minDanger[0] <= self.position[0] and minDanger[1] >= self.position[1]):
                distX = 1
                distY = -1
            elif (minDanger[0] >= self.position[0] and minDanger[1] <= self.position[1]):
                distX = -1
                distY = 1
            elif(minDanger[0] >= self.position[0] and minDanger[1] >= self.position[1]):
                distX = -1
                distY = -1

        temp = keepInsideMap(distX, distY, self.position[0], self.position[1], diameter)


        return temp[0], temp[1]
